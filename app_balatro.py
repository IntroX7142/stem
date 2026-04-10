from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv
import io
import json
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
    "THCS Minh Đức (Đồng Nai)": (10.95, 107.01),
    "TP.HCM": (10.7769, 106.7009),
    "Hà Nội": (21.0285, 105.8542),
}

OBJECT_CATEGORIES = {
    "Mat Troi": "He Mat Troi", "Mat Trang": "He Mat Troi",
    "Sao Thuy": "He Mat Troi", "Sao Kim": "He Mat Troi",
    "Sao Hoa": "He Mat Troi", "Sao Moc": "He Mat Troi",
    "Sao Tho": "He Mat Troi",
    "Polaris": "Sao sang", "Sirius": "Sao sang", "Vega": "Sao sang",
    "Orion": "Chom sao", "Cassiopeia": "Chom sao",
    "Andromeda": "Thien ha",
}

# ==================== FUN FACTS & DISPLAY ====================
FUN_FACTS = { ... }  # giữ nguyên như cũ (đã có đầy đủ)
DISPLAY_NAMES = { ... }  # giữ nguyên như cũ

def apply_theme():
    st.markdown("""<style>
    .stApp { background: radial-gradient(circle at 10% -10%, #1e293b 0%, #0f172a 45%, #020617 100%); color: #e5e7eb; }
    .block-container { max-width: 1280px; padding-top: 1.8rem; }
    h1, h2, h3 { color: #e0f2fe !important; letter-spacing: -0.4px; }
    [data-testid="stMetric"] { background: rgba(15,23,42,0.8); border: 1px solid rgba(125,211,252,0.3); border-radius: 16px; padding: 16px 14px; }
    .stButton > button { background: linear-gradient(90deg, #22d3ee, #38bdf8) !important; color: #082f49 !important; font-weight: 700; border-radius: 12px; }
    .guide, .warn { border-radius: 14px; padding: 14px; margin: 12px 0; }
    .guide { background: rgba(6,78,59,0.25); border: 1px solid rgba(16,185,129,0.5); }
    .warn { background: rgba(127,29,29,0.25); border: 1px solid rgba(248,113,113,0.5); }
    </style>""", unsafe_allow_html=True)

# ==================== SKYFIELD RESOURCES ====================
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
        "Polaris": Star(ra_hours=2.53, dec_degrees=89.26),
        "Sirius": Star(ra_hours=6.7525, dec_degrees=-16.7161),
        "Vega": Star(ra_hours=18.6167, dec_degrees=38.7833),
        "Orion": Star(ra_hours=5.5, dec_degrees=0.0),
        "Cassiopeia": Star(ra_hours=1.0, dec_degrees=62.0),
        "Andromeda": Star(ra_hours=0.7, dec_degrees=41.2),
    }

def compute_alt_az(obj, observer, t):
    astrometric = observer.at(t).observe(obj)
    alt, az, distance = astrometric.apparent().altaz()
    return alt.degrees, az.degrees, distance

# ==================== CACHE SNAPSHOT ====================
@st.cache_data(ttl=60, show_spinner=False)
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
        rows.append({
            "Thien the": name, "Nhom": OBJECT_CATEGORIES.get(name, "Khac"),
            "Altitude": round(alt, 1), "Azimuth": round(az, 1),
            "Trang thai": "Có thể quan sát" if visible else "Dưới chân trời",
            "visible": visible
        })

        # Timeline
        tl = []
        for m in range(0, horizon_hours * 60 + 1, step_minutes):
            dt_utc = now_utc + timedelta(minutes=m)
            alt_m, az_m, _ = compute_alt_az(obj, observer, ts.from_datetime(dt_utc))
            tl.append({
                "time": dt_utc.astimezone(LOCAL_TZ).strftime("%H:%M"),
                "alt": round(alt_m, 2),
                "az": round(az_m, 2)
            })
        timelines[name] = tl

        best = max(tl, key=lambda x: x["alt"])
        vis_pct = round(100 * len([x for x in tl if x["alt"] > 0]) / len(tl), 1)
        score = round(best["alt"] * 0.7 + vis_pct * 0.3, 2)
        planner.append({
            "Muc tieu": name, "Nhom": OBJECT_CATEGORIES.get(name, "Khac"),
            "Diem uu tien": score,
            "Do cao cuc dai": best["alt"],
            "Ty le nhin thay (%)": vis_pct,
            "Gio nen ngam": best["time"]
        })

    planner = sorted(planner, key=lambda x: x["Diem uu tien"], reverse=True)[:8]
    return rows, timelines, planner

# ==================== CHARTS ====================
def make_chart(rows, only_visible):
    fig = go.Figure()
    colors = {"He Mat Troi": "#22d3ee", "Sao sang": "#c026d3", "Chom sao": "#f472b6", "Thien ha": "#34d399"}

    for r in rows:
        if only_visible and not r["visible"]:
            continue
        cat = OBJECT_CATEGORIES.get(r["Thien the"], "Khac")
        color = colors.get(cat, "#64748b")
        fig.add_trace(go.Scatter(
            x=[r["Azimuth"]], y=[r["Altitude"]],
            mode="markers+text",
            text=[DISPLAY_NAMES.get(r["Thien the"], r["Thien the"])],
            textposition="top center",
            marker=dict(size=16 if r["visible"] else 11, color=color,
                        line=dict(color="white", width=1.5)),
            name=cat,
            showlegend=True
        ))

    fig.update_layout(
        height=480,
        title="🌌 Bản đồ sao (Alt-Az)",
        xaxis_title="Phương vị (Azimuth °)",
        yaxis_title="Độ cao (Altitude °)",
        xaxis=dict(
            tickmode="array",
            tickvals=[0, 45, 90, 135, 180, 225, 270, 315, 360],
            ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"],
            range=[0, 360]
        ),
        yaxis=dict(range=[-8, 92]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#e5e7eb", opacity=0.6)
    return fig

def make_timeline_chart(timelines, target):
    if target not in timelines:
        return None
    tl = timelines[target]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[x["time"] for x in tl],
        y=[x["alt"] for x in tl],
        mode="lines+markers",
        line=dict(color="#22d3ee", width=3),
        marker=dict(size=6),
        name="Độ cao"
    ))
    fig.update_layout(
        height=380,
        title=f"📈 Độ cao {DISPLAY_NAMES.get(target, target)} trong {len(tl)*15//60} giờ tới",
        xaxis_title="Thời gian (GMT+7)",
        yaxis_title="Độ cao (°)",
        yaxis=dict(range=[-10, 92]),
        plot_bgcolor="rgba(15,23,42,0.6)"
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#e5e7eb")
    return fig

# ==================== PROFILES ====================
def load_profiles():
    if Path(PROFILE_STORE).exists():
        try:
            with open(PROFILE_STORE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_profiles(profiles):
    with open(PROFILE_STORE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

# ==================== SIDEBAR ====================
def sidebar():
    with st.sidebar:
        st.header("⚙️ Cấu hình quan sát")

        # === PROFILES ===
        st.subheader("📋 Hồ sơ quan sát")
        if "profiles" not in st.session_state:
            st.session_state.profiles = load_profiles()

        profile_list = list(st.session_state.profiles.keys())
        if profile_list:
            selected_profile = st.selectbox("Tải hồ sơ", ["-- Chọn --"] + profile_list, key="load_profile")
            if selected_profile != "-- Chọn --" and st.button("✅ Áp dụng hồ sơ"):
                lat_val, lon_val = st.session_state.profiles[selected_profile]
                st.session_state.current_lat = lat_val
                st.session_state.current_lon = lon_val
                st.success(f"Đã áp dụng **{selected_profile}**")
                st.rerun()

        # === LOCATION ===
        preset = st.selectbox("📍 Chọn địa điểm", list(LOCATION_PRESETS.keys()) + ["Tùy chỉnh"], key="preset")
        if preset != "Tùy chỉnh":
            station = preset
            d_lat, d_lon = LOCATION_PRESETS[preset]
        else:
            station = "Trạm tùy chỉnh"
            d_lat, d_lon = DEFAULT_LAT, DEFAULT_LON

        # Sử dụng session_state để giữ giá trị khi áp dụng profile
        lat = st.number_input("Vĩ độ", -90.0, 90.0, st.session_state.get("current_lat", d_lat), 0.001, format="%.4f", key="lat_input")
        lon = st.number_input("Kinh độ", -180.0, 180.0, st.session_state.get("current_lon", d_lon), 0.001, format="%.4f", key="lon_input")

        h = st.slider("Khung dự báo (giờ)", 3, 24, 12, 1)
        step = st.slider("Bước tính (phút)", 5, 60, 15, 5)

        st.divider()
        new_name = st.text_input("Tên hồ sơ mới", value=station, key="new_profile_name")
        if st.button("💾 Lưu vị trí hiện tại"):
            if new_name:
                st.session_state.profiles[new_name] = (lat, lon)
                save_profiles(st.session_state.profiles)
                st.success(f"✅ Đã lưu hồ sơ **{new_name}**")
                st.rerun()

        return station, lat, lon, h, step

# ==================== MAIN ====================
def main():
    st.set_page_config(page_title="Kính Thiên Văn STEM", page_icon="🔭", layout="wide")
    apply_theme()
    st.title("🔭 Kính Thiên Văn STEM")
    st.caption("🌌 Quan sát thời gian thực • Dễ dùng cho lớp học STEM • Đã nâng cấp 2026")

    station, lat, lon, horizon_hours, step_minutes = sidebar()

    minute_bucket = int(datetime.now(timezone.utc).timestamp() // 60)

    planets, earth, ts = get_resources()
    db = build_db(planets)
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)

    rows, timelines, planner = snapshot(lat, lon, horizon_hours, step_minutes, minute_bucket)

    st.write(f"📍 **Trạm:** {station} | **Tọa độ:** {lat:.4f}, {lon:.4f} | 🕒 **{datetime.now(LOCAL_TZ).strftime('%d/%m/%Y %H:%M:%S')}**")

    col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 1])
    vis = len([r for r in rows if r["visible"]])
    col1.metric("✅ Đang quan sát được", f"{vis}/{len(rows)}")
    col2.metric("📅 Planner", len(planner))
    col3.metric("🧭 Tổng đối tượng", len(rows))
    if col4.button("🔄 Làm mới dữ liệu", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Filters
    f1, f2, f3 = st.columns([2, 2, 1])
    group = f1.selectbox("🔎 Lọc nhóm", ["Tất cả", "He Mat Troi", "Sao sang", "Chom sao", "Thien ha"], key="group")
    search = f2.text_input("🔍 Tìm thiên thể", "", key="search")
    only_visible = f3.toggle("Chỉ hiện đang thấy", False, key="only_visible")

    names = [n for n in db.keys() if (group == "Tất cả" or OBJECT_CATEGORIES.get(n, "") == group) and (search.strip().lower() in n.lower())]
    target = st.selectbox("🪐 Chọn thiên thể", names or list(db.keys()), key="target", format_func=lambda x: DISPLAY_NAMES.get(x, x))

    if st.button("📍 Dò tìm & quan sát", type="primary", use_container_width=True):
        alt, az, dist = compute_alt_az(db[target], observer, ts.now())
        dist_text = f"{dist.km:,.0f} km" if hasattr(dist, "km") else "Khoảng cách rất lớn"
        st.session_state.scan = {"target": target, "alt": alt, "az": az, "dist": dist_text}

    # === KẾT QUẢ QUAN SÁT ===
    if "scan" in st.session_state:
        r = st.session_state.scan
        k1, k2 = st.columns(2)
        k1.metric("🌍 Độ cao", f"{r['alt']:.1f}°")
        k2.metric("🧭 Phương vị", f"{r['az']:.1f}°")
        st.info(f"📏 Khoảng cách: **{r['dist']}**")

        if timelines.get(r["target"]):
            best = max(timelines[r["target"]], key=lambda x: x["alt"])
            st.info(f"⏰ Giờ đề xuất: **{best['time']}** (độ cao cực đại **{best['alt']:.1f}°**)")

        st.plotly_chart(make_timeline_chart(timelines, r["target"]), use_container_width=True)

        # Hướng dẫn
        if r["alt"] > 0:
            st.markdown(f"""
            <div class='guide'>
            <b>🎯 Hướng dẫn chỉnh kính:</b><br>
            1) Xoay chân đế hướng <b>{r['az']:.0f}°</b> (Bắc = 0°)<br>
            2) Nâng ống kính lên <b>{r['alt']:.0f}°</b><br>
            3) Căn tâm bằng kính ngắm → chỉnh nét focus
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='warn'>Mục tiêu đang dưới chân trời. Hãy đợi thêm!</div>", unsafe_allow_html=True)

        st.write(f"**🌟 Fun fact:** {FUN_FACTS.get(r['target'], 'Hãy tiếp tục khám phá vũ trụ!')}")

    # === TABS ===
    tab1, tab2, tab3 = st.tabs(["🌌 Bản đồ sao", "📅 Kế hoạch quan sát", "📊 Tổng quan"])

    with tab1:
        st.plotly_chart(make_chart(rows, only_visible), use_container_width=True)

    with tab2:
        planner_df = pd.DataFrame(planner)
        st.dataframe(planner_df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Tải Planner CSV", data=to_csv_bytes(planner), file_name="planner.csv", mime="text/csv")
        st.download_button("⬇️ Tải Planner Excel", data=to_excel_bytes(planner_df), file_name="planner.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with tab3:
        summary_rows = [{k: v for k, v in r.items() if k != "visible"} for r in rows]
        summary_df = pd.DataFrame(summary_rows)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Tải Tổng quan CSV", data=to_csv_bytes(summary_rows), file_name="summary.csv", mime="text/csv")
        st.download_button("⬇️ Tải Tổng quan Excel", data=to_excel_bytes(summary_df), file_name="summary.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Helper functions (giữ nguyên)
def to_csv_bytes(rows): 
    if not rows: return b""
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

if __name__ == "__main__":
    main()
