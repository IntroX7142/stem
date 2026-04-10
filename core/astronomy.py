from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import time

import streamlit as st
from skyfield.api import Loader, Topos, load

from core.constants import FIXED_TARGET_COORDS, LOCAL_TZ, OBJECT_CATEGORIES, SOLAR_SYSTEM_KEYS
from data.catalog import build_celestial_db

try:
    from astroplan import FixedTarget, Observer
    from astropy import units as u
    from astropy.coordinates import EarthLocation, SkyCoord
    from astropy.time import Time as AstroTime

    ASTROPLAN_AVAILABLE = True
except Exception:
    ASTROPLAN_AVAILABLE = False


def _debug_log(hypothesis_id, location, message, data=None, run_id="pre-fix"):
    payload = {
        "sessionId": "82ac6d",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    try:
        with open("debug-82ac6d.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


@st.cache_resource(show_spinner=False)
def get_astronomy_resources():
    errors = []

    # Thu cach mac dinh cua Skyfield truoc.
    try:
        planets = load("de421.bsp")
        ts = load.timescale()
        return planets, planets["earth"], ts
    except Exception as exc:
        errors.append(f"default-loader: {exc}")

    # Fallback tren thu muc tam (tranh loi quyen ghi tren Streamlit Cloud).
    try:
        skyfield_tmp = Path(tempfile.gettempdir()) / "skyfield_data_cache"
        skyfield_tmp.mkdir(parents=True, exist_ok=True)
        loader = Loader(str(skyfield_tmp))
        planets = loader("de421.bsp")
        ts = loader.timescale()
        return planets, planets["earth"], ts
    except Exception as exc:
        errors.append(f"tmp-loader: {exc}")

    raise RuntimeError(
        "Khong tai duoc du lieu thien van de421.bsp. "
        "Co the host nguon du lieu bi chan/khong truy cap duoc. "
        f"Chi tiet: {' | '.join(errors)}"
    )


def build_observer(earth, latitude, longitude):
    return earth + Topos(latitude_degrees=latitude, longitude_degrees=longitude)


def compute_alt_az(obj, observer, t):
    astrometric = observer.at(t).observe(obj)
    alt, az, distance = astrometric.apparent().altaz()
    return alt.degrees, az.degrees, distance


def tinh_toan_vi_tri(thien_the_chon, db_thien_the, observer, ts):
    obj = db_thien_the[thien_the_chon]
    alt, az, distance = compute_alt_az(obj, observer, ts.now())
    if thien_the_chon in SOLAR_SYSTEM_KEYS and hasattr(distance, "km"):
        return alt, az, f"{distance.km:,.0f} km"
    return alt, az, "Xa vô tận (hàng trăm năm ánh sáng)"


@st.cache_data(ttl=90, show_spinner=False)
def compute_cached_engine(latitude, longitude, horizon_hours, step_minutes, minute_bucket):
    # #region agent log
    _debug_log(
        "H1_cache_unserializable",
        "core/astronomy.py:compute_cached_engine",
        "compute_cached_engine called",
        {
            "latitude": latitude,
            "longitude": longitude,
            "horizon_hours": horizon_hours,
            "step_minutes": step_minutes,
            "minute_bucket": minute_bucket,
        },
    )
    # #endregion
    planets, earth, ts = get_astronomy_resources()
    db_thien_the = build_celestial_db(planets)
    observer = build_observer(earth, latitude, longitude)
    t_now = ts.now()
    now_utc = datetime.now(timezone.utc)

    snapshot_rows = []
    timeline_by_target = {}
    planner_rows = []

    for name, obj in db_thien_the.items():
        alt, az, _ = compute_alt_az(obj, observer, t_now)
        visible = alt > 0
        snapshot_rows.append(
            {
                "Thiên thể": name,
                "Nhóm": OBJECT_CATEGORIES.get(name, "Khác"),
                "Altitude (°)": round(alt, 1),
                "Azimuth (°)": round(az, 1),
                "Trạng thái": "Có thể quan sát" if visible else "Dưới chân trời",
                "Ưu tiên": "Cao" if alt > 30 else ("Trung bình" if alt > 10 else "Thấp"),
                "visible": visible,
            }
        )

        timeline = []
        for minute in range(0, horizon_hours * 60 + 1, step_minutes):
            dt_utc = now_utc + timedelta(minutes=minute)
            alt_m, az_m, _ = compute_alt_az(obj, observer, ts.from_datetime(dt_utc))
            timeline.append({"time": dt_utc.astimezone(LOCAL_TZ).strftime("%H:%M"), "alt": round(alt_m, 2), "az": round(az_m, 2)})
        timeline_by_target[name] = timeline

        if OBJECT_CATEGORIES.get(name) != "Thiên hà":
            max_alt = max(point["alt"] for point in timeline)
            best_time = max(timeline, key=lambda point: point["alt"])["time"]
            visible_points = sum(1 for point in timeline if point["alt"] > 0)
            visibility_ratio = visible_points / max(len(timeline), 1)
            score = max_alt * 0.7 + visibility_ratio * 100 * 0.3
            planner_rows.append(
                {
                    "Mục tiêu": name,
                    "Nhóm": OBJECT_CATEGORIES.get(name, "Khác"),
                    "Điểm ưu tiên": round(score, 2),
                    "Độ cao cực đại (°)": round(max_alt, 1),
                    "Tỷ lệ nhìn thấy (%)": round(visibility_ratio * 100, 1),
                    "Giờ nên ngắm (GMT+7)": best_time,
                }
            )

    planner_rows = sorted(planner_rows, key=lambda row: row["Điểm ưu tiên"], reverse=True)[:8]
    # #region agent log
    _debug_log(
        "H2_return_shape",
        "core/astronomy.py:compute_cached_engine",
        "compute_cached_engine return shape",
        {
            "snapshot_len": len(snapshot_rows),
            "planner_len": len(planner_rows),
            "timeline_targets": len(timeline_by_target),
        },
    )
    # #endregion
    return snapshot_rows, planner_rows, timeline_by_target


def get_rise_set_info(target_name, latitude, longitude):
    if not ASTROPLAN_AVAILABLE:
        return "Chưa bật", "Cài thêm astropy + astroplan để xem giờ mọc/lặn."
    try:
        location = EarthLocation.from_geodetic(longitude * u.deg, latitude * u.deg)
        observer = Observer(location=location, timezone="Asia/Ho_Chi_Minh")
        now = AstroTime.now()
        if target_name == "☀️ MẶT TRỜI":
            rise_time = observer.sun_rise_time(now, which="next")
            set_time = observer.sun_set_time(now, which="next")
        elif target_name == "🌕 MẶT TRĂNG":
            rise_time = observer.moon_rise_time(now, which="next")
            set_time = observer.moon_set_time(now, which="next")
        elif target_name in FIXED_TARGET_COORDS:
            ra_hours, dec_deg = FIXED_TARGET_COORDS[target_name]
            coord = SkyCoord(ra=ra_hours * u.hourangle, dec=dec_deg * u.deg, frame="icrs")
            target = FixedTarget(name=target_name, coord=coord)
            rise_time = observer.target_rise_time(now, target, which="next")
            set_time = observer.target_set_time(now, target, which="next")
        else:
            return "Giới hạn", "Mới hỗ trợ mọc/lặn cho Mặt Trời, Mặt Trăng và mục tiêu cố định."
        rise_local = rise_time.to_datetime(timezone=LOCAL_TZ).strftime("%H:%M")
        set_local = set_time.to_datetime(timezone=LOCAL_TZ).strftime("%H:%M")
        return "Sẵn sàng", f"Mọc: {rise_local} • Lặn: {set_local} (GMT+7)"
    except Exception:
        return "Không khả dụng", "Không tính được giờ mọc/lặn tại vị trí hiện tại."
