from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv
import io
import tempfile

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from skyfield.api import Loader, Star, Topos, load

LOCAL_TZ = timezone(timedelta(hours=7))
DEFAULT_LAT = 10.95
DEFAULT_LON = 107.01
PROFILE_STORE = "observer_profiles.json"

LOCATION_PRESETS = {
    "THCS Minh Duc (Dong Nai)": (10.95, 107.01),
    "TP.HCM": (10.7769, 106.7009),
    "Ha Noi": (21.0285, 105.8542),
}

OBJECT_CATEGORIES = {
    "Mat Troi": "He Mat Troi",
    "Mat Trang": "He Mat Troi",
    "Sao Thuy": "He Mat Troi",
    "Sao Kim": "He Mat Troi",
    "Sao Hoa": "He Mat Troi",
    "Sao Moc": "He Mat Troi",
    "Sao Tho": "He Mat Troi",
    "Polaris": "Sao sang",
    "Sirius": "Sao sang",
    "Vega": "Sao sang",
    "Orion": "Chom sao",
    "Cassiopeia": "Chom sao",
    "Andromeda": "Thien ha",
}

FUN_FACTS = {
    "Mat Troi": "Anh sang Mat Troi den Trai Dat sau khoang 8 phut 20 giay.",
    "Mat Trang": "Mat Trang dang roi xa Trai Dat khoang 3.8 cm moi nam.",
    "Sao Hoa": "Sao Hoa co Olympus Mons, nui lua lon nhat He Mat Troi.",
    "Polaris": "Polaris gan cuc Bac thien cau, dung de dinh huong huong Bac.",
}


def apply_theme():
    st.markdown(
        """
    <style>
    .stApp { background: linear-gradient(180deg, #0f172a 0%, #111827 100%); color: #e5e7eb; }
    .block-container { max-width: 1200px; padding-top: 1.4rem; }
    .guide { background: rgba(6, 78, 59, 0.25); border: 1px solid rgba(16, 185, 129, 0.45); border-radius: 12px; padding: 12px; margin: 10px 0; }
    .warn { background: rgba(127, 29, 29, 0.25); border: 1px solid rgba(248, 113, 113, 0.45); border-radius: 12px; padding: 12px; margin: 10px 0; }
    </style>
    """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def get_resources():
    try:
        planets = load("de421.bsp")
        ts = load.timescale()
        return planets, planets["earth"], ts
    except Exception:
        cache_dir = Path(tempfile.gettempdir()) / "skyfield_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        loader = Loader(str(cache_dir))
        planets = loader("de421.bsp")
        ts = loader.timescale()
        return planets, planets["earth"], ts


def build_db(planets):
    return {
        "Mat Troi": planets["sun"],
        "Mat Trang": planets["moon"],
        "Sao Thuy": planets["mercury"],
        "Sao Kim": planets["venus"],
        "Sao Hoa": planets["mars"],
        "Sao Moc": planets["jupiter barycenter"],
        "Sao Tho": planets["saturn barycenter"],
        "Orion": Star(ra_hours=5.5, dec_degrees=0.0),
        "Cassiopeia": Star(ra_hours=1.0, dec_degrees=62.0),
        "Polaris": Star(ra_hours=2.53, dec_degrees=89.26),
        "Sirius": Star(ra_hours=6.7525, dec_degrees=-16.7161),
        "Vega": Star(ra_hours=18.6167, dec_degrees=38.7833),
        "Andromeda": Star(ra_hours=0.7, dec_degrees=41.2),
    }


def compute_alt_az(obj, observer, t):
    astrometric = observer.at(t).observe(obj)
    alt, az, distance = astrometric.apparent().altaz()
    return alt.degrees, az.degrees, distance


@st.cache_data(ttl=90, show_spinner=False)
def snapshot(lat, lon, horizon_hours, step_minutes, minute_bucket):
    planets, earth, ts = get_resources()
    db = build_db(planets)
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
    now_utc = datetime.now(timezone.utc)
    t_now = ts.now()

    rows, timelines, planner = [], {}, []
    for name, obj in db.items():
        alt, az, _ = compute_alt_az(obj, observer, t_now)
        visible = alt > 0
        rows.append({"Thien the": name, "Nhom": OBJECT_CATEGORIES.get(name, "Khac"), "Altitude": round(alt, 1), "Azimuth": round(az, 1), "Trang thai": "Co the quan sat" if visible else "Duoi chan troi", "visible": visible})
        tl = []
        for m in range(0, horizon_hours * 60 + 1, step_minutes):
            dt_utc = now_utc + timedelta(minutes=m)
            alt_m, az_m, _ = compute_alt_az(obj, observer, ts.from_datetime(dt_utc))
            tl.append({"time": dt_utc.astimezone(LOCAL_TZ).strftime("%H:%M"), "alt": round(alt_m, 2), "az": round(az_m, 2)})
        timelines[name] = tl
        best = max(tl, key=lambda x: x["alt"])
        vis_pct = round(100 * len([x for x in tl if x["alt"] > 0]) / len(tl), 1)
        score = round(best["alt"] * 0.7 + vis_pct * 0.3, 2)
        planner.append({"Muc tieu": name, "Nhom": OBJECT_CATEGORIES.get(name, "Khac"), "Diem uu tien": score, "Do cao cuc dai": best["alt"], "Ty le nhin thay (%)": vis_pct, "Gio nen ngam": best["time"]})

    planner = sorted(planner, key=lambda x: x["Diem uu tien"], reverse=True)[:8]
    return rows, timelines, planner


def make_chart(rows, only_visible):
    fig = go.Figure()
    for r in rows:
        if only_visible and not r["visible"]:
            continue
        fig.add_trace(go.Scatter(x=[r["Azimuth"]], y=[r["Altitude"]], mode="markers+text", text=[r["Thien the"]], textposition="top center", marker=dict(size=14 if r["visible"] else 9, color="#22d3ee" if r["visible"] else "#64748b"), showlegend=False))
    fig.add_hline(y=0, line_dash="dash", line_color="#e5e7eb")
    fig.update_layout(height=460, title="Ban do sao", xaxis_title="Phuong vi (do)", yaxis_title="Do cao (do)")
    return fig


def to_csv_bytes(rows):
    if not rows:
        return b""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def to_excel_bytes(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="data")
    return out.getvalue()


def render_guidance(target, alt, az):
    st.markdown("### 🎯 Hướng dẫn chỉnh kính sau khi dò tìm")
    if alt > 0:
        text = (
            f"1) Xoay chân đế hướng **{az:.0f}°** (Bắc = 0°).  \n"
            f"2) Nâng ống kính lên **{alt:.0f}°**.  \n"
            "3) Căn tâm bằng kính ngắm, sau đó chỉnh nét bằng vòng focus."
        )
        st.markdown(f"<div class='guide'>{text}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='warn'>Mục tiêu đang dưới chân trời, hãy đợi thêm và thử lại.</div>", unsafe_allow_html=True)


def sidebar():
    with st.sidebar:
        st.header("⚙️ Cấu hình quan sát")
        preset = st.selectbox("📍 Chọn địa điểm", list(LOCATION_PRESETS.keys()) + ["Tùy chỉnh"], key="preset")
        if preset != "Tùy chỉnh":
            station = preset
            d_lat, d_lon = LOCATION_PRESETS[preset]
        else:
            station = st.text_input("Tên trạm", "Trạm tùy chỉnh")
            d_lat, d_lon = DEFAULT_LAT, DEFAULT_LON
        lat = st.number_input("Vĩ độ", -90.0, 90.0, d_lat, 0.001, format="%.4f")
        lon = st.number_input("Kinh độ", -180.0, 180.0, d_lon, 0.001, format="%.4f")
        h = st.slider("Khung dự báo (giờ)", 3, 24, 12, 1)
        step = st.slider("Bước tính (phút)", 5, 60, 15, 5)
    return station, lat, lon, h, step


def main():
    st.set_page_config(page_title="Kính Thiên Văn STEM", page_icon="🌌", layout="wide")
    apply_theme()
    st.title("🌌 Kính Thiên Văn STEM")
    st.caption("Giao diện gọn, rõ ràng, dễ dùng cho lớp học STEM")

    station, lat, lon, horizon_hours, step_minutes = sidebar()
    minute_bucket = int(datetime.now(timezone.utc).timestamp() // 60)
    try:
        planets, earth, ts = get_resources()
        db = build_db(planets)
        observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
        rows, timelines, planner = snapshot(lat, lon, horizon_hours, step_minutes, minute_bucket)
    except Exception as exc:
        st.error("❌ Không tải được dữ liệu thiên văn.")
        st.code(str(exc))
        st.stop()

    st.write(f"**Trạm:** {station} | **Tọa độ:** {lat:.4f}, {lon:.4f} | **Giờ:** {datetime.now(LOCAL_TZ).strftime('%d/%m/%Y %H:%M:%S')}")

    m1, m2, m3 = st.columns(3)
    vis = len([r for r in rows if r["visible"]])
    m1.metric("Đang quan sát được", f"{vis}/{len(rows)}")
    m2.metric("Mục tiêu planner", len(planner))
    m3.metric("Tổng đối tượng", len(rows))

    f1, f2, f3 = st.columns([2, 2, 1])
    group = f1.selectbox("Lọc nhóm", ["Tất cả", "He Mat Troi", "Sao sang", "Chom sao", "Thien ha"], key="group")
    search = f2.text_input("Tìm thiên thể", "", key="search")
    only_visible = f3.toggle("Chỉ hiện đang thấy", False, key="only_visible")
    names = [n for n in db.keys() if (group == "Tất cả" or OBJECT_CATEGORIES.get(n, "") == group) and (search.strip().lower() in n.lower())]
    if not names:
        names = list(db.keys())
    target = st.selectbox("🪐 Chọn thiên thể", names, key="target")

    if st.button("📍 Dò tìm và quan sát", use_container_width=True):
        alt, az, dist = compute_alt_az(db[target], observer, ts.now())
        dist_text = f"{dist.km:,.0f} km" if hasattr(dist, "km") else "Khoang cach lon"
        st.session_state.scan = {"target": target, "alt": alt, "az": az, "dist": dist_text}

    if "scan" in st.session_state:
        r = st.session_state.scan
        k1, k2 = st.columns(2)
        k1.metric("Độ cao", f"{r['alt']:.1f}°")
        k2.metric("Phương vị", f"{r['az']:.1f}°")
        st.info(f"📏 Khoảng cách ước tính: {r['dist']}")
        if timelines.get(r["target"]):
            best = max(timelines[r["target"]], key=lambda x: x["alt"])
            st.info(f"⏱️ Giờ đề xuất: {best['time']} (GMT+7), độ cao cực đại {best['alt']:.1f}°")
        render_guidance(r["target"], r["alt"], r["az"])
        st.write(f"**🌟 Fun fact:** {FUN_FACTS.get(r['target'], 'Hãy tiếp tục khám phá vũ trụ!')}")

    tab1, tab2, tab3 = st.tabs(["🌌 Bản đồ sao", "📅 Planner", "📊 Tổng quan"])
    with tab1:
        st.plotly_chart(make_chart(rows, only_visible), use_container_width=True)
    with tab2:
        planner_df = pd.DataFrame(planner)
        st.dataframe(planner_df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Tải planner CSV", data=to_csv_bytes(planner), file_name="planner.csv", mime="text/csv")
        st.download_button("⬇️ Tải planner Excel", data=to_excel_bytes(planner_df), file_name="planner.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with tab3:
        summary_rows = [{k: v for k, v in r.items() if k != "visible"} for r in rows]
        summary_df = pd.DataFrame(summary_rows)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Tải tổng quan CSV", data=to_csv_bytes(summary_rows), file_name="summary.csv", mime="text/csv")
        st.download_button("⬇️ Tải tổng quan Excel", data=to_excel_bytes(summary_df), file_name="summary.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if __name__ == "__main__":
    main()
