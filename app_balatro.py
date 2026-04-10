from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv
import html
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
    "🏫 THCS Minh Đức (Đồng Nai)": (10.95, 107.01),
    "🏙️ TP.HCM": (10.7769, 106.7009),
    "🏛️ Hà Nội": (21.0285, 105.8542),
}

OBJECT_CATEGORIES = {
    "☀️ Mặt Trời": "Hệ Mặt Trời",
    "🌕 Mặt Trăng": "Hệ Mặt Trời",
    "🪐 Sao Thủy": "Hệ Mặt Trời",
    "🪐 Sao Kim": "Hệ Mặt Trời",
    "🪐 Sao Hỏa": "Hệ Mặt Trời",
    "🪐 Sao Mộc": "Hệ Mặt Trời",
    "🪐 Sao Thổ": "Hệ Mặt Trời",
    "🪐 Sao Thiên Vương": "Hệ Mặt Trời",
    "🪐 Sao Hải Vương": "Hệ Mặt Trời",
    "⭐ Sao Bắc Cực (Polaris)": "Sao sáng",
    "⭐ Sao Sirius": "Sao sáng",
    "⭐ Sao Vega": "Sao sáng",
    "⭐ Sao Betelgeuse": "Sao sáng",
    "⭐ Sao Rigel": "Sao sáng",
    "⭐ Sao Aldebaran": "Sao sáng",
    "⭐ Sao Antares": "Sao sáng",
    "⭐ Sao Deneb": "Sao sáng",
    "⭐ Sao Altair": "Sao sáng",
    "⭐ Sao Arcturus": "Sao sáng",
    "✨ Chòm Orion": "Chòm sao",
    "✨ Chòm Cassiopeia": "Chòm sao",
    "✨ Chòm Gấu Lớn": "Chòm sao",
    "✨ Chòm Bọ Cạp": "Chòm sao",
    "✨ Chòm Sư Tử": "Chòm sao",
    "✨ Chòm Thiên Nga": "Chòm sao",
    "🌀 Thiên hà Andromeda": "Thiên hà",
}

FUN_FACTS = {
    "☀️ Mặt Trời": "Ánh sáng từ Mặt Trời đến Trái Đất sau khoảng 8 phút 20 giây.",
    "🌕 Mặt Trăng": "Mặt Trăng đang rời xa Trái Đất khoảng 3.8 cm mỗi năm.",
    "🪐 Sao Thủy": "Sao Thủy quay quanh Mặt Trời rất nhanh, chỉ khoảng 88 ngày.",
    "🪐 Sao Kim": "Sao Kim quay ngược chiều và có khí quyển dày, rất nóng.",
    "🪐 Sao Hỏa": "Sao Hỏa có núi Olympus Mons, núi lửa lớn nhất Hệ Mặt Trời.",
    "🪐 Sao Mộc": "Sao Mộc có Vết Đỏ Lớn, một cơn bão khổng lồ kéo dài hàng thế kỷ.",
    "🪐 Sao Thổ": "Sao Thổ nổi bật với hệ vành đai băng đá tuyệt đẹp.",
    "🪐 Sao Thiên Vương": "Sao Thiên Vương quay nghiêng gần như nằm ngang.",
    "🪐 Sao Hải Vương": "Sao Hải Vương có gió cực mạnh trong Hệ Mặt Trời.",
    "⭐ Sao Bắc Cực (Polaris)": "Polaris nằm gần cực Bắc thiên cầu nên rất hữu ích để định hướng.",
    "⭐ Sao Sirius": "Sirius là sao sáng nhất trên bầu trời đêm khi nhìn từ Trái Đất.",
    "⭐ Sao Vega": "Vega từng là sao Bắc Cực trong quá khứ xa.",
    "⭐ Sao Betelgeuse": "Betelgeuse là sao khổng lồ đỏ nổi bật trong chòm Orion.",
    "⭐ Sao Rigel": "Rigel là một trong các sao sáng nhất của chòm Orion.",
    "⭐ Sao Aldebaran": "Aldebaran có màu cam đỏ đặc trưng và khá dễ nhận ra.",
    "⭐ Sao Antares": "Antares là sao sáng đỏ nổi bật của chòm Bọ Cạp.",
    "⭐ Sao Deneb": "Deneb là một đỉnh của Tam giác Mùa Hè.",
    "⭐ Sao Altair": "Altair là sao sáng chính trong chòm Đại Bàng.",
    "⭐ Sao Arcturus": "Arcturus là sao rất sáng thuộc chòm Mục Phu.",
    "✨ Chòm Orion": "Chòm Orion dễ nhận ra nhờ ba sao thẳng hàng ở phần đai.",
    "✨ Chòm Cassiopeia": "Cassiopeia có dạng chữ W đặc trưng ở bầu trời phía Bắc.",
    "✨ Chòm Gấu Lớn": "Chòm Gấu Lớn chứa nhóm sao Bắc Đẩu nổi tiếng.",
    "✨ Chòm Bọ Cạp": "Chòm Bọ Cạp nổi bật vào mùa hè với sao Antares màu đỏ.",
    "✨ Chòm Sư Tử": "Chòm Sư Tử thường quan sát tốt vào mùa xuân.",
    "✨ Chòm Thiên Nga": "Chòm Thiên Nga có hình chữ thập lớn dễ định vị.",
    "🌀 Thiên hà Andromeda": "Andromeda là thiên hà lớn gần Ngân Hà và có thể thấy mờ trong trời tối.",
}


def apply_theme():
    st.markdown(
        """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
    :root {
        --bg-deep: #030712;
        --bg-mid: #0c1222;
        --accent: #22d3ee;
        --accent-soft: rgba(34, 211, 238, 0.15);
        --glow: rgba(56, 189, 248, 0.35);
        --text: #e2e8f0;
        --muted: #94a3b8;
        --card: rgba(15, 23, 42, 0.65);
        --border: rgba(125, 211, 252, 0.22);
    }
    html, body, [class*="css"] { font-family: 'Outfit', system-ui, sans-serif !important; }
    .stApp {
        background-color: var(--bg-deep);
        background-image:
            radial-gradient(ellipse 120% 80% at 50% -30%, rgba(56, 189, 248, 0.12) 0%, transparent 55%),
            radial-gradient(circle at 85% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 10% 60%, rgba(34, 211, 238, 0.06) 0%, transparent 35%);
        color: var(--text);
    }
    .block-container { max-width: 1180px; padding-top: 1.25rem; padding-bottom: 2.5rem; }
    h1 { font-weight: 700 !important; letter-spacing: -0.04em !important; font-size: 2.15rem !important; }
    h1, h2, h3 { color: #f0f9ff !important; }
    h2, h3 { font-weight: 600 !important; letter-spacing: -0.02em !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.92) 0%, rgba(3, 7, 18, 0.96) 100%) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        font-size: 1.05rem !important; color: #bae6fd !important;
    }
    [data-testid="stMetric"] {
        background: var(--card) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 1rem 1rem !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
    }
    [data-testid="stMetric"] label { color: var(--muted) !important; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #f0f9ff !important; font-weight: 700 !important; }
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        box-shadow: 0 4px 20px var(--glow);
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 28px rgba(56, 189, 248, 0.45) !important;
        color: #fff !important;
    }
    .stDownloadButton > button {
        background: rgba(30, 41, 59, 0.9) !important;
        color: #e0f2fe !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
    }
    .stDownloadButton > button:hover { border-color: var(--accent) !important; color: #fff !important; }
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stSlider label { color: #cbd5e1 !important; font-weight: 500 !important; }
    [data-baseweb="select"] > div, [data-baseweb="input"] > div {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-color: var(--border) !important;
        border-radius: 10px !important;
    }
    .stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"] { color: var(--muted) !important; }
    [data-testid="stTab"] { font-weight: 600 !important; color: var(--muted) !important; }
    [data-testid="stTab"][aria-selected="true"] { color: var(--accent) !important; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(15, 23, 42, 0.5) !important;
        border-radius: 14px !important;
        padding: 6px !important;
        border: 1px solid var(--border) !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
    }
    div[data-testid="stExpander"] { border: 1px solid var(--border); border-radius: 12px; background: var(--card); }
    .hero-wrap {
        position: relative;
        padding: 1.35rem 1.5rem 1.5rem;
        margin-bottom: 1.35rem;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 27, 75, 0.35) 100%);
        border: 1px solid var(--border);
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.06);
        overflow: hidden;
    }
    .hero-wrap::before {
        content: "";
        position: absolute;
        top: -50%; right: -20%;
        width: 55%; height: 200%;
        background: radial-gradient(circle, rgba(34, 211, 238, 0.12) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        margin: 0 0 0.35rem 0;
        background: linear-gradient(90deg, #f0f9ff 0%, #7dd3fc 45%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-sub { color: #94a3b8; font-size: 0.98rem; margin: 0; line-height: 1.5; max-width: 52ch; }
    .station-bar {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #bae6fd;
        background: rgba(2, 6, 23, 0.55);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0 1.25rem 0;
    }
    .card-panel {
        background: var(--card);
        backdrop-filter: blur(8px);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem 1.15rem;
        margin: 0.75rem 0 1rem 0;
    }
    .scan-heading {
        color: #7dd3fc;
        font-weight: 600;
        font-size: 1.05rem;
        margin: 0.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border);
    }
    .guide {
        background: linear-gradient(90deg, rgba(6, 78, 59, 0.35), rgba(15, 23, 42, 0.4));
        border: 1px solid rgba(52, 211, 153, 0.4);
        border-radius: 14px;
        padding: 14px 16px;
        margin: 10px 0;
        line-height: 1.65;
    }
    .warn {
        background: linear-gradient(90deg, rgba(127, 29, 29, 0.35), rgba(15, 23, 42, 0.4));
        border: 1px solid rgba(248, 113, 113, 0.45);
        border-radius: 14px;
        padding: 14px 16px;
        margin: 10px 0;
    }
    div[data-testid="stNotification"], [data-testid="stAlert"] { border-radius: 12px !important; }
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
        "☀️ Mặt Trời": planets["sun"],
        "🌕 Mặt Trăng": planets["moon"],
        "🪐 Sao Thủy": planets["mercury"],
        "🪐 Sao Kim": planets["venus"],
        "🪐 Sao Hỏa": planets["mars"],
        "🪐 Sao Mộc": planets["jupiter barycenter"],
        "🪐 Sao Thổ": planets["saturn barycenter"],
        "🪐 Sao Thiên Vương": planets["uranus barycenter"],
        "🪐 Sao Hải Vương": planets["neptune barycenter"],
        "⭐ Sao Bắc Cực (Polaris)": Star(ra_hours=2.53, dec_degrees=89.26),
        "⭐ Sao Sirius": Star(ra_hours=6.7525, dec_degrees=-16.7161),
        "⭐ Sao Vega": Star(ra_hours=18.6167, dec_degrees=38.7833),
        "⭐ Sao Betelgeuse": Star(ra_hours=5.9195, dec_degrees=7.4073),
        "⭐ Sao Rigel": Star(ra_hours=5.2423, dec_degrees=-8.2016),
        "⭐ Sao Aldebaran": Star(ra_hours=4.5987, dec_degrees=16.5093),
        "⭐ Sao Antares": Star(ra_hours=16.4901, dec_degrees=-26.4319),
        "⭐ Sao Deneb": Star(ra_hours=20.6905, dec_degrees=45.2803),
        "⭐ Sao Altair": Star(ra_hours=19.8464, dec_degrees=8.8683),
        "⭐ Sao Arcturus": Star(ra_hours=14.261, dec_degrees=19.1824),
        "✨ Chòm Orion": Star(ra_hours=5.5, dec_degrees=0.0),
        "✨ Chòm Cassiopeia": Star(ra_hours=1.0, dec_degrees=62.0),
        "✨ Chòm Gấu Lớn": Star(ra_hours=11.0, dec_degrees=50.0),
        "✨ Chòm Bọ Cạp": Star(ra_hours=16.8, dec_degrees=-30.0),
        "✨ Chòm Sư Tử": Star(ra_hours=10.5, dec_degrees=15.0),
        "✨ Chòm Thiên Nga": Star(ra_hours=20.7, dec_degrees=40.0),
        "🌀 Thiên hà Andromeda": Star(ra_hours=0.7, dec_degrees=41.2),
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
        fig.add_trace(
            go.Scatter(
                x=[r["Azimuth"]],
                y=[r["Altitude"]],
                mode="markers+text",
                text=[r["Thien the"]],
                textposition="top center",
                textfont=dict(size=11, color="#e2e8f0"),
                marker=dict(
                    size=16 if r["visible"] else 10,
                    color="#22d3ee" if r["visible"] else "#475569",
                    line=dict(width=1, color="rgba(255,255,255,0.25)"),
                ),
                showlegend=False,
            )
        )
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(148, 163, 184, 0.6)", line_width=1)
    fig.update_layout(
        template="plotly_dark",
        height=480,
        title=dict(text="Bản đồ sao — phương vị & độ cao", font=dict(size=17, color="#f0f9ff")),
        xaxis_title="Phương vị (°)",
        yaxis_title="Độ cao (°)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.45)",
        font=dict(family="Outfit, sans-serif", color="#cbd5e1"),
        margin=dict(t=56, b=48, l=56, r=24),
        xaxis=dict(gridcolor="rgba(148, 163, 184, 0.12)", zeroline=False),
        yaxis=dict(gridcolor="rgba(148, 163, 184, 0.12)", zeroline=False, range=[-10, 95]),
    )
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
        st.markdown("### ⚙️ Cấu hình")
        st.caption("Địa điểm & khung thời gian tính toán")
        preset = st.selectbox("📍 Chọn địa điểm quan sát", list(LOCATION_PRESETS.keys()) + ["🛠️ Tùy chỉnh"], key="preset")
        if preset != "🛠️ Tùy chỉnh":
            station = preset
            d_lat, d_lon = LOCATION_PRESETS[preset]
        else:
            station = st.text_input("Tên trạm", "🛰️ Trạm tùy chỉnh")
            d_lat, d_lon = DEFAULT_LAT, DEFAULT_LON
        lat = st.number_input("Vĩ độ", -90.0, 90.0, d_lat, 0.001, format="%.4f")
        lon = st.number_input("Kinh độ", -180.0, 180.0, d_lon, 0.001, format="%.4f")
        h = st.slider("Khung dự báo (giờ)", 3, 24, 12, 1)
        step = st.slider("Bước tính (phút)", 5, 60, 15, 5)
    return station, lat, lon, h, step


def main():
    st.set_page_config(page_title="Kính Thiên Văn STEM", page_icon="🔭", layout="wide", initial_sidebar_state="expanded")
    apply_theme()
    st.markdown(
        """
        <div class="hero-wrap">
            <p class="hero-title">🔭 Kính Thiên Văn STEM</p>
            <p class="hero-sub">Giao diện cho lớp học: dò thiên thể, bản đồ sao và kế hoạch quan sát theo thời gian thực — dễ đọc, dễ thao tác.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

    now_str = datetime.now(LOCAL_TZ).strftime("%d/%m/%Y %H:%M:%S")
    st.markdown(
        f'<div class="station-bar">📍 Trạm: <strong style="color:#e0f2fe">{html.escape(station)}</strong> &nbsp;·&nbsp; '
        f"φ {lat:.4f}° λ {lon:.4f}° &nbsp;·&nbsp; 🕒 {html.escape(now_str)}</div>",
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)
    vis = len([r for r in rows if r["visible"]])
    m1.metric("✅ Đang quan sát được", f"{vis}/{len(rows)}")
    m2.metric("📅 Mục tiêu planner", len(planner))
    m3.metric("🧭 Tổng đối tượng", len(rows))

    st.markdown("#### Chọn mục tiêu")
    f1, f2, f3 = st.columns([2, 2, 1])
    group = f1.selectbox("🔎 Lọc nhóm", ["Tất cả", "Hệ Mặt Trời", "Sao sáng", "Chòm sao", "Thiên hà"], key="group")
    search = f2.text_input("Tìm thiên thể", "", key="search", placeholder="Gõ tên sao, hành tinh…")
    only_visible = f3.toggle("Chỉ hiện đang thấy", False, key="only_visible")
    names = [n for n in db.keys() if (group == "Tất cả" or OBJECT_CATEGORIES.get(n, "") == group) and (search.strip().lower() in n.lower())]
    if not names:
        names = list(db.keys())
    target = st.selectbox("🪐 Chọn thiên thể", names, key="target")

    if st.button("📍 Dò tìm & quan sát", use_container_width=True):
        alt, az, dist = compute_alt_az(db[target], observer, ts.now())
        dist_text = f"{dist.km:,.0f} km" if hasattr(dist, "km") else "Khoảng cách rất xa"
        st.session_state.scan = {"target": target, "alt": alt, "az": az, "dist": dist_text}

    if "scan" in st.session_state:
        r = st.session_state.scan
        st.markdown(f'<div class="scan-heading">Kết quả dò — {html.escape(r["target"])}</div>', unsafe_allow_html=True)
        k1, k2 = st.columns(2)
        k1.metric("Độ cao", f"{r['alt']:.1f}°")
        k2.metric("Phương vị", f"{r['az']:.1f}°")
        st.info(f"📏 Khoảng cách ước tính: {r['dist']}")
        if timelines.get(r["target"]):
            best = max(timelines[r["target"]], key=lambda x: x["alt"])
            st.info(f"⏱️ Giờ đề xuất: {best['time']} (GMT+7), độ cao cực đại {best['alt']:.1f}°")
        render_guidance(r["target"], r["alt"], r["az"])
        fact = html.escape(FUN_FACTS.get(r["target"], "Hãy tiếp tục khám phá vũ trụ!"))
        st.markdown(
            f'<div class="card-panel"><p style="margin:0;color:#e2e8f0;"><strong style="color:#fde68a;">🌟 Fun fact</strong><br/>{fact}</p></div>',
            unsafe_allow_html=True,
        )

    # Đảm bảo bộ dữ liệu fun fact luôn đầy đủ cho các thiên thể đang sử dụng.
    missing_facts = [name for name in db.keys() if name not in FUN_FACTS]
    if missing_facts:
        st.warning("Thiếu Fun Fact cho: " + ", ".join(missing_facts))

    tab1, tab2, tab3, tab4 = st.tabs(["🌌 Bản đồ sao", "📅 Kế hoạch quan sát", "📊 Tổng quan", "🏆 Xếp hạng thiên thể"])
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

    with tab4:
        st.subheader("🏆 Bảng xếp hạng thiên thể quan sát tốt nhất")
        bang_xep_hang = []
        for ten, du_lieu_tuyen_tinh in timelines.items():
            do_cao_cuc_dai = max(m["alt"] for m in du_lieu_tuyen_tinh)
            so_moc_nhin_thay = len([m for m in du_lieu_tuyen_tinh if m["alt"] > 0])
            ty_le_nhin_thay = round(100 * so_moc_nhin_thay / len(du_lieu_tuyen_tinh), 1) if du_lieu_tuyen_tinh else 0.0
            diem_uu_tien = round(do_cao_cuc_dai * 0.7 + ty_le_nhin_thay * 0.3, 2)
            trang_thai_hien_tai = next((r["Trang thai"] for r in rows if r["Thien the"] == ten), "Không rõ")
            bang_xep_hang.append(
                {
                    "Thiên thể": ten,
                    "Nhóm": OBJECT_CATEGORIES.get(ten, "Khác"),
                    "Điểm ưu tiên": diem_uu_tien,
                    "Độ cao cực đại (°)": round(do_cao_cuc_dai, 1),
                    "Tỷ lệ nhìn thấy (%)": ty_le_nhin_thay,
                    "Trạng thái hiện tại": trang_thai_hien_tai,
                }
            )
        bang_xep_hang_df = pd.DataFrame(bang_xep_hang).sort_values(by="Điểm ưu tiên", ascending=False).reset_index(drop=True)
        bang_xep_hang_df.index = bang_xep_hang_df.index + 1
        st.dataframe(bang_xep_hang_df, use_container_width=True)
        st.markdown("### ⭐ Top 5 ưu tiên ngay")
        for hang, dong in bang_xep_hang_df.head(5).iterrows():
            st.write(f"{hang}. {dong['Thiên thể']} — Điểm {dong['Điểm ưu tiên']} • Độ cao tối đa {dong['Độ cao cực đại (°)']}°")
        st.download_button(
            "⬇️ Tải bảng xếp hạng CSV",
            data=to_csv_bytes(bang_xep_hang_df.to_dict(orient="records")),
            file_name="bang_xep_hang_thien_the.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.caption("✨ Sản phẩm STEM của lớp 9.1 — Viết bằng Python, Streamlit và Skyfield")


if __name__ == "__main__":
    main()
