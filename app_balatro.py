from datetime import datetime, timedelta, timezone
import csv
import io

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from skyfield.api import Star, Topos, load
try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

try:
    from astroplan import FixedTarget, Observer
    from astropy import units as u
    from astropy.coordinates import EarthLocation, SkyCoord
    from astropy.time import Time as AstroTime

    ASTROPLAN_AVAILABLE = True
except Exception:
    ASTROPLAN_AVAILABLE = False

# ====================== CẤU HÌNH VỊ TRÍ QUAN SÁT ======================
DEFAULT_LAT = 10.9500
DEFAULT_LON = 107.0100
LOCAL_TZ = timezone(timedelta(hours=7))
SOLAR_SYSTEM_KEYS = {
    "☀️ MẶT TRỜI",
    "🌕 MẶT TRĂNG",
    "🪐 Sao Thủy (Mercury)",
    "🪐 Sao Kim (Venus)",
    "🪐 Sao Hỏa (Mars)",
    "🪐 Sao Mộc (Jupiter)",
    "🪐 Sao Thổ (Saturn)",
    "🪐 Sao Thiên Vương (Uranus)",
    "🪐 Sao Hải Vương (Neptune)",
}
OBJECT_CATEGORIES = {
    "☀️ MẶT TRỜI": "Hệ Mặt Trời",
    "🌕 MẶT TRĂNG": "Hệ Mặt Trời",
    "🪐 Sao Thủy (Mercury)": "Hệ Mặt Trời",
    "🪐 Sao Kim (Venus)": "Hệ Mặt Trời",
    "🪐 Sao Hỏa (Mars)": "Hệ Mặt Trời",
    "🪐 Sao Mộc (Jupiter)": "Hệ Mặt Trời",
    "🪐 Sao Thổ (Saturn)": "Hệ Mặt Trời",
    "🪐 Sao Thiên Vương (Uranus)": "Hệ Mặt Trời",
    "🪐 Sao Hải Vương (Neptune)": "Hệ Mặt Trời",
    "✨ Chòm Gấu Lớn (Ursa Major)": "Chòm sao",
    "✨ Chòm Thợ Săn (Orion)": "Chòm sao",
    "✨ Chòm Bọ Cạp (Scorpius)": "Chòm sao",
    "✨ Chòm Cassiopeia": "Chòm sao",
    "✨ Chòm Sư Tử (Leo)": "Chòm sao",
    "✨ Chòm Thiên Nga (Cygnus)": "Chòm sao",
    "⭐️ Sao Bắc Cực (Polaris)": "Sao sáng",
    "⭐️ Sao Sirius": "Sao sáng",
    "⭐️ Sao Betelgeuse": "Sao sáng",
    "⭐️ Sao Vega": "Sao sáng",
    "🌀 Thiên hà Andromeda (M31)": "Thiên hà",
    "🌀 Tâm Ngân Hà (Milky Way Center)": "Thiên hà",
}
LOCATION_PRESETS = {
    "THCS Minh Đức (Đồng Nai)": (10.9500, 107.0100),
    "TP.HCM": (10.7769, 106.7009),
    "Hà Nội": (21.0285, 105.8542),
    "Đà Nẵng": (16.0544, 108.2022),
    "Cần Thơ": (10.0452, 105.7469),
    "Nha Trang": (12.2388, 109.1967),
}
FIXED_TARGET_COORDS = {
    "✨ Chòm Gấu Lớn (Ursa Major)": (11.0, 50.0),
    "✨ Chòm Thợ Săn (Orion)": (5.5, 0.0),
    "✨ Chòm Bọ Cạp (Scorpius)": (16.8, -30.0),
    "✨ Chòm Cassiopeia": (1.0, 62.0),
    "✨ Chòm Sư Tử (Leo)": (10.5, 15.0),
    "✨ Chòm Thiên Nga (Cygnus)": (20.7, 40.0),
    "⭐️ Sao Bắc Cực (Polaris)": (2.53, 89.26),
    "⭐️ Sao Sirius": (6.7525, -16.7161),
    "⭐️ Sao Betelgeuse": (5.9195, 7.4073),
    "⭐️ Sao Vega": (18.6167, 38.7833),
    "🌀 Thiên hà Andromeda (M31)": (0.7, 41.2),
    "🌀 Tâm Ngân Hà (Milky Way Center)": (17.75, -29.0),
}


@st.cache_resource(show_spinner=False)
def get_astronomy_resources():
    planets = load("de421.bsp")
    ts = load.timescale()
    return planets, planets["earth"], ts


def build_celestial_db(planets):
    return {
        # Hệ Mặt Trời
        "☀️ MẶT TRỜI": planets["sun"],
        "🌕 MẶT TRĂNG": planets["moon"],
        "🪐 Sao Thủy (Mercury)": planets["mercury"],
        "🪐 Sao Kim (Venus)": planets["venus"],
        "🪐 Sao Hỏa (Mars)": planets["mars"],
        "🪐 Sao Mộc (Jupiter)": planets["jupiter barycenter"],
        "🪐 Sao Thổ (Saturn)": planets["saturn barycenter"],
        "🪐 Sao Thiên Vương (Uranus)": planets["uranus barycenter"],
        "🪐 Sao Hải Vương (Neptune)": planets["neptune barycenter"],
        # Chòm sao & Sao sáng
        "✨ Chòm Gấu Lớn (Ursa Major)": Star(ra_hours=11.0, dec_degrees=50.0),
        "✨ Chòm Thợ Săn (Orion)": Star(ra_hours=5.5, dec_degrees=0.0),
        "✨ Chòm Bọ Cạp (Scorpius)": Star(ra_hours=16.8, dec_degrees=-30.0),
        "✨ Chòm Cassiopeia": Star(ra_hours=1.0, dec_degrees=62.0),
        "✨ Chòm Sư Tử (Leo)": Star(ra_hours=10.5, dec_degrees=15.0),
        "✨ Chòm Thiên Nga (Cygnus)": Star(ra_hours=20.7, dec_degrees=40.0),
        "⭐️ Sao Bắc Cực (Polaris)": Star(ra_hours=2.53, dec_degrees=89.26),
        "⭐️ Sao Sirius": Star(ra_hours=6.7525, dec_degrees=-16.7161),
        "⭐️ Sao Betelgeuse": Star(ra_hours=5.9195, dec_degrees=7.4073),
        "⭐️ Sao Vega": Star(ra_hours=18.6167, dec_degrees=38.7833),
        # Thiên hà
        "🌀 Thiên hà Andromeda (M31)": Star(ra_hours=0.7, dec_degrees=41.2),
        "🌀 Tâm Ngân Hà (Milky Way Center)": Star(ra_hours=17.75, dec_degrees=-29.0),
    }


# ====================== FUN FACTS (Mỗi thiên thể có sự thật thú vị) ======================
fun_facts = {
    "☀️ MẶT TRỜI": "Mặt Trời chiếm 99.8% khối lượng Hệ Mặt Trời! Ánh sáng từ Mặt Trời mất đúng 8 phút 20 giây để đến Trái Đất.",
    "🌕 MẶT TRĂNG": "Mặt Trăng đang rời xa Trái Đất 3.8 cm mỗi năm! Nó có diện tích bề mặt bằng châu Phi.",
    "🪐 Sao Thủy (Mercury)": "Sao Thủy quay quanh Mặt Trời chỉ trong 88 ngày Trái Đất và có nhiệt độ dao động từ -173°C đến 427°C.",
    "🪐 Sao Kim (Venus)": "Sao Kim quay ngược chiều so với các hành tinh khác và có khí quyển độc hại nhất Hệ Mặt Trời.",
    "🪐 Sao Hỏa (Mars)": "Trên Sao Hỏa có ngọn núi cao nhất Hệ Mặt Trời: Olympus Mons cao gấp 3 lần Everest!",
    "🪐 Sao Mộc (Jupiter)": "Sao Mộc có hơn 95 mặt trăng và có Cơn bão Lớn Đỏ tồn tại hơn 300 năm.",
    "🪐 Sao Thổ (Saturn)": "Sao Thổ có hệ vành đai đẹp nhất Hệ Mặt Trời, làm từ băng và đá.",
    "🪐 Sao Thiên Vương (Uranus)": "Sao Thiên Vương quay nghiêng 98° so với mặt phẳng quỹ đạo - giống như đang 'nằm ngang'.",
    "🪐 Sao Hải Vương (Neptune)": "Gió trên Sao Hải Vương thổi mạnh nhất Hệ Mặt Trời, lên đến 2.100 km/h!",
    "✨ Chòm Gấu Lớn (Ursa Major)": "Chòm Gấu Lớn chứa 'Bắc Đẩu' - 7 sao sáng giúp định hướng từ hàng ngàn năm trước.",
    "✨ Chòm Thợ Săn (Orion)": "Đai Thợ Săn gồm 3 sao thẳng hàng, và đây là nơi có Tinh vân Orion - khu vực sinh sao lớn nhất gần chúng ta.",
    "✨ Chòm Bọ Cạp (Scorpius)": "Chứa sao Antares - 'Đối thủ của Ares' - một siêu sao khổng lồ đỏ sắp nổ thành siêu tân tinh.",
    "✨ Chòm Cassiopeia": "Hình chữ W hoặc M, dễ nhận biết ở bán cầu Bắc. Trong thần thoại, Cassiopeia là nữ hoàng kiêu ngạo.",
    "✨ Chòm Sư Tử (Leo)": "Chứa sao Regulus - 'Trái tim sư tử'. Chòm sao này xuất hiện vào mùa xuân.",
    "✨ Chòm Thiên Nga (Cygnus)": "Hình chữ thập khổng lồ, chứa sao Deneb - một trong những sao sáng nhất bầu trời đêm.",
    "⭐️ Sao Bắc Cực (Polaris)": "Polaris nằm gần cực Bắc bầu trời, nên luôn chỉ hướng Bắc. Nó cách Trái Đất 323 năm ánh sáng.",
    "⭐️ Sao Sirius": "Sirius là sao sáng nhất bầu trời đêm, cách chúng ta chỉ 8.6 năm ánh sáng. Người Ai Cập cổ đại coi nó là 'Ngôi sao của Isis'.",
    "⭐️ Sao Betelgeuse": "Betelgeuse là sao khổng lồ đỏ trong Orion, nếu đặt ở vị trí Mặt Trời thì nó sẽ nuốt chửng cả sao Thủy đến sao Hỏa!",
    "⭐️ Sao Vega": "Vega từng là Sao Bắc Cực cách đây 12.000 năm và sẽ lại là Sao Bắc Cực trong tương lai.",
    "🌀 Thiên hà Andromeda (M31)": "Andromeda là thiên hà lớn nhất láng giềng, cách 2.5 triệu năm ánh sáng và đang lao về phía Ngân Hà!",
    "🌀 Tâm Ngân Hà (Milky Way Center)": "Trung tâm Ngân Hà chứa hố đen siêu nặng Sagittarius A* với khối lượng bằng 4 triệu Mặt Trời.",
}


# ====================== HÀM TÍNH TOÁN CHUNG ======================
def compute_alt_az(obj, observer, t):
    astrometric = observer.at(t).observe(obj)
    alt, az, distance = astrometric.apparent().altaz()
    return alt.degrees, az.degrees, distance


def build_observer(earth, latitude, longitude):
    return earth + Topos(latitude_degrees=latitude, longitude_degrees=longitude)


def tinh_toan_vi_tri(thien_the_chon, db_thien_the, observer, ts):
    doi_tuong = db_thien_the[thien_the_chon]
    t = ts.now()
    alt, az, distance = compute_alt_az(doi_tuong, observer, t)
    if thien_the_chon in SOLAR_SYSTEM_KEYS and hasattr(distance, "km"):
        dist_str = f"{distance.km:,.0f} km"
    else:
        dist_str = "Xa vô tận (hàng trăm năm ánh sáng)"
    return alt, az, dist_str


def best_observation_time(thien_the_chon, db_thien_the, observer, ts, horizon_hours=12, step_minutes=15):
    obj = db_thien_the[thien_the_chon]
    now_utc = datetime.now(timezone.utc)
    best_alt = -999.0
    best_dt_utc = now_utc
    for minute in range(0, horizon_hours * 60 + 1, step_minutes):
        dt_utc = now_utc + timedelta(minutes=minute)
        t = ts.from_datetime(dt_utc)
        alt, _, _ = compute_alt_az(obj, observer, t)
        if alt > best_alt:
            best_alt = alt
            best_dt_utc = dt_utc
    return best_dt_utc.astimezone(LOCAL_TZ), best_alt


def build_timeline_for_object(obj, observer, ts, horizon_hours=12, step_minutes=30):
    now_utc = datetime.now(timezone.utc)
    points = []
    for minute in range(0, horizon_hours * 60 + 1, step_minutes):
        dt_utc = now_utc + timedelta(minutes=minute)
        t = ts.from_datetime(dt_utc)
        alt, az, _ = compute_alt_az(obj, observer, t)
        points.append({"time": dt_utc.astimezone(LOCAL_TZ).strftime("%H:%M"), "alt": round(alt, 2), "az": round(az, 2)})
    return points


def next_visibility_window(obj, observer, ts, horizon_hours=12, step_minutes=10):
    now_utc = datetime.now(timezone.utc)
    first_visible = None
    first_hidden = None
    for minute in range(0, horizon_hours * 60 + 1, step_minutes):
        dt_utc = now_utc + timedelta(minutes=minute)
        t = ts.from_datetime(dt_utc)
        alt, _, _ = compute_alt_az(obj, observer, t)
        if alt > 0 and first_visible is None:
            first_visible = dt_utc
        if first_visible is not None and alt <= 0:
            first_hidden = dt_utc
            break
    return first_visible, first_hidden


def score_target_for_tonight(name, db_thien_the, observer, ts, horizon_hours=12, step_minutes=15):
    obj = db_thien_the[name]
    timeline = build_timeline_for_object(obj, observer, ts, horizon_hours=horizon_hours, step_minutes=step_minutes)
    max_alt = max(point["alt"] for point in timeline)
    best_time = max(timeline, key=lambda point: point["alt"])["time"]
    visible_points = sum(1 for point in timeline if point["alt"] > 0)
    visibility_ratio = visible_points / max(len(timeline), 1)
    # Score đơn giản để ưu tiên mục tiêu cao và quan sát được lâu.
    score = max_alt * 0.7 + visibility_ratio * 100 * 0.3
    return round(score, 2), round(max_alt, 1), round(visibility_ratio * 100, 1), best_time


def create_csv_bytes(rows):
    buffer = io.StringIO()
    if not rows:
        return "".encode("utf-8")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def create_excel_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="planner")
    return output.getvalue()


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
            fixed_target = FixedTarget(name=target_name, coord=coord)
            rise_time = observer.target_rise_time(now, fixed_target, which="next")
            set_time = observer.target_set_time(now, fixed_target, which="next")
        else:
            return "Giới hạn", "Hiện mới hỗ trợ mọc/lặn cho Mặt Trời, Mặt Trăng, sao/chòm sao/thiên hà cố định."

        rise_local = rise_time.to_datetime(timezone=LOCAL_TZ).strftime("%H:%M")
        set_local = set_time.to_datetime(timezone=LOCAL_TZ).strftime("%H:%M")
        return "Sẵn sàng", f"Mọc: {rise_local} • Lặn: {set_local} (GMT+7)"
    except Exception:
        return "Không khả dụng", "Không tính được giờ mọc/lặn cho mục tiêu này tại vị trí hiện tại."


def build_sky_snapshot_rows(db_thien_the, observer, t):
    rows = []
    for ten, obj in db_thien_the.items():
        alt, az, _ = compute_alt_az(obj, observer, t)
        visible = alt > 0
        rows.append(
            {
                "Thiên thể": ten,
                "Nhóm": OBJECT_CATEGORIES.get(ten, "Khác"),
                "Altitude (°)": round(alt, 1),
                "Azimuth (°)": round(az, 1),
                "Trạng thái": "Có thể quan sát" if visible else "Dưới chân trời",
                "Ưu tiên": "Cao" if alt > 30 else ("Trung bình" if alt > 10 else "Thấp"),
                "visible": visible,
            }
        )
    return rows


def ve_ban_do_sao_tuong_tac(rows, only_visible=False):
    fig = go.Figure()
    filtered_rows = []
    for row in rows:
        ten = row["Thiên thể"]
        alt = row["Altitude (°)"]
        az = row["Azimuth (°)"]
        visible = row["visible"]
        if only_visible and not visible:
            continue
        filtered_rows.append(row)
        color = "#67e8f9" if visible else "#64748b"
        size = 18 if visible else 10
        symbol = "star" if ("✨" in ten or "⭐️" in ten) else "circle"
        fact_snippet = fun_facts.get(ten, "Khám phá vũ trụ!")[:80] + "..."
        hover_text = (
            f"<b>{ten}</b><br>"
            f"Độ cao: <b>{alt:.1f}°</b><br>"
            f"Phương vị: <b>{az:.1f}°</b><br>"
            f"Trạng thái: {'<span style=\"color:#67e8f9\">VISIBLE</span>' if visible else 'Dưới chân trời'}<br>"
            f"Fun fact: {fact_snippet}"
        )
        short_name = ten.split(" ", 1)[1] if " " in ten else ten
        fig.add_trace(
            go.Scatter(
                x=[az],
                y=[alt],
                mode="markers+text",
                marker=dict(size=size, color=color, symbol=symbol, line=dict(width=2, color="white")),
                text=[short_name[:14]],
                textposition="top center",
                hovertemplate=hover_text + "<extra></extra>",
                name=ten,
                showlegend=False,
            )
        )
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#f1faee",
        line_width=2,
        annotation_text="🌅 CHÂN TRỜI",
        annotation_position="bottom right",
        annotation_font=dict(color="#f1faee", size=14),
    )
    fig.update_layout(
        title="🌌 BẢN ĐỒ SAO TƯƠNG TÁC – Bầu trời Minh Đức (thời gian thực)",
        xaxis=dict(
            title="Phương vị (Azimuth °)",
            range=[0, 360],
            tickvals=[0, 45, 90, 135, 180, 225, 270, 315, 360],
            ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"],
            gridcolor="rgba(255,255,255,0.1)",
        ),
        yaxis=dict(title="Độ cao (Altitude °)", range=[-15, 90], gridcolor="rgba(255,255,255,0.1)"),
        plot_bgcolor="rgba(10, 5, 31, 0.85)",
        paper_bgcolor="rgba(10, 5, 31, 0)",
        height=520,
        margin=dict(l=50, r=30, t=70, b=50),
        font=dict(family="Inter", color="#f0f9ff", size=14),
    )
    return fig, filtered_rows

# ====================== Giao diện ======================
def apply_modern_dark_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle at 20% -10%, #18223d 0%, #0d1428 45%, #090f1d 100%);
        font-family: 'Inter', system-ui, sans-serif;
        color: #e6edf7;
    }
    
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    h1 {
        font-size: 2.6rem !important;
        font-weight: 700;
        letter-spacing: -1px;
        color: #dbeafe !important;
        text-shadow: none;
    }
    
    .subtitle {
        font-size: 1rem;
        color: #9fb0cc;
        text-align: center;
        font-weight: 500;
        margin-top: -10px;
        margin-bottom: 8px;
    }
    
    .section-card {
        background: linear-gradient(180deg, rgba(20, 30, 52, 0.85) 0%, rgba(12, 20, 38, 0.9) 100%);
        border: 1px solid rgba(125, 160, 220, 0.22);
        border-radius: 16px;
        padding: 14px 18px;
        margin: 8px 0 16px;
    }
    
    [data-testid="stMetric"] {
        background: rgba(16, 26, 44, 0.75) !important;
        border: 1px solid rgba(125, 160, 220, 0.3) !important;
        border-radius: 16px !important;
        padding: 18px !important;
        box-shadow: none !important;
    }
    
    [data-testid="stMetricLabel"] { color: #9fb0cc !important; }
    [data-testid="stMetricValue"] { font-size: 2.1rem !important; color: #7dd3fc !important; }
    
    .stButton > button {
        background: #38bdf8 !important;
        color: #06101f !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.65rem 1rem !important;
    }
    
    .stButton > button:hover {
        background: #0ea5e9 !important;
        color: #f8fbff !important;
    }
    
    .stSelectbox div[data-baseweb="select"],
    div[data-baseweb="input"],
    div[data-baseweb="base-input"] {
        background-color: rgba(11, 20, 37, 0.95) !important;
        border: 1px solid rgba(125, 160, 220, 0.35) !important;
        border-radius: 12px !important;
        color: #e6edf7 !important;
    }
    
    .fun-fact {
        background: rgba(12, 22, 39, 0.85);
        border: 1px solid rgba(125, 160, 220, 0.35);
        border-radius: 14px;
        padding: 16px 18px;
        margin: 16px 0 8px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid rgba(125, 160, 220, 0.25);
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# ====================== CHƯƠNG TRÌNH CHÍNH ======================
st.set_page_config(page_title="Kính Thiên Văn Thông Minh", page_icon="🌌", layout="wide", initial_sidebar_state="collapsed")
apply_modern_dark_theme()
st.title("⭐️ KÍNH THIÊN VĂN THÔNG MINH ⭐️")
st.markdown("<p class='subtitle'>TRẠM QUAN SÁT: THCS MINH ĐỨC • ĐỒNG NAI • THỜI GIAN THỰC</p>", unsafe_allow_html=True)
st.markdown("---")

try:
    planets, earth, ts = get_astronomy_resources()
except Exception:
    st.error("Không thể tải dữ liệu thiên văn (de421.bsp). Hãy kiểm tra mạng và chạy lại ứng dụng.")
    st.stop()

db_thien_the = build_celestial_db(planets)
with st.sidebar:
    st.header("⚙️ Cấu hình quan sát")
    selected_preset = st.selectbox("Preset địa điểm", list(LOCATION_PRESETS.keys()) + ["Tùy chỉnh"])
    if selected_preset == "Tùy chỉnh":
        station_name = st.text_input("Tên trạm", value="Trạm tùy chỉnh")
        default_lat, default_lon = DEFAULT_LAT, DEFAULT_LON
    else:
        station_name = selected_preset
        default_lat, default_lon = LOCATION_PRESETS[selected_preset]
    latitude = st.number_input("Vĩ độ", min_value=-90.0, max_value=90.0, value=default_lat, step=0.001, format="%.4f")
    longitude = st.number_input("Kinh độ", min_value=-180.0, max_value=180.0, value=default_lon, step=0.001, format="%.4f")
    horizon_hours = st.slider("Khung dự báo (giờ)", min_value=3, max_value=24, value=12, step=1)
    plan_step = st.slider("Bước lập kế hoạch (phút)", min_value=5, max_value=60, value=15, step=5)

observer = build_observer(earth, latitude, longitude)
st.caption(
    f"📍 Trạm: **{station_name}** • Vị trí: **{latitude:.4f}, {longitude:.4f}** • "
    f"Giờ địa phương: **{datetime.now(LOCAL_TZ).strftime('%d/%m/%Y %H:%M:%S')} (GMT+7)**"
)

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
ctl_col1, ctl_col2, ctl_col3, ctl_col4 = st.columns([2, 1, 1, 1])
with ctl_col1:
    category_choice = st.selectbox("Nhóm thiên thể", ["Tất cả", "Hệ Mặt Trời", "Chòm sao", "Sao sáng", "Thiên hà"])
with ctl_col2:
    search_text = st.text_input("Tìm nhanh", value="", placeholder="Ví dụ: Sirius")
with ctl_col3:
    only_visible = st.toggle("Chỉ hiện mục đang nhìn thấy", value=False)
with ctl_col4:
    auto_refresh = st.toggle("Tự động cập nhật", value=False)
st.markdown("</div>", unsafe_allow_html=True)

filtered_names = []
for name in db_thien_the:
    in_category = category_choice == "Tất cả" or OBJECT_CATEGORIES.get(name) == category_choice
    in_search = search_text.strip().lower() in name.lower()
    if in_category and in_search:
        filtered_names.append(name)
if not filtered_names:
    filtered_names = list(db_thien_the.keys())
lua_chon = st.selectbox("🪐 CHỌN MỤC TIÊU CỦA BẠN:", filtered_names, label_visibility="visible")

refresh_seconds = 20
if auto_refresh:
    refresh_seconds = st.slider("Chu kỳ làm mới (giây)", min_value=10, max_value=120, value=20, step=5)
    if st_autorefresh is not None:
        st_autorefresh(interval=refresh_seconds * 1000, key="auto_refresh_timer")
    else:
        st.info("Để auto-refresh mượt hơn, cài thêm thư viện `streamlit-autorefresh`.")

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if st.button("📍 BẮT ĐẦU DÒ TÌM & QUAN SÁT", use_container_width=True):
    try:
        alt, az, khoang_cach_str = tinh_toan_vi_tri(lua_chon, db_thien_the, observer, ts)
    except Exception:
        st.error("Không thể tính vị trí thiên thể lúc này. Vui lòng thử lại sau vài giây.")
        st.stop()
    st.session_state.last_result = {"name": lua_chon, "alt": alt, "az": az, "dist": khoang_cach_str}

if st.session_state.last_result:
    lua_chon = st.session_state.last_result["name"]
    alt = st.session_state.last_result["alt"]
    az = st.session_state.last_result["az"]
    khoang_cach_str = st.session_state.last_result["dist"]
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🌍 ĐỘ CAO (Altitude)", value=f"{alt:.1f}°")
    with col2:
        st.metric(label="🧭 PHƯƠNG VỊ (Azimuth)", value=f"{az:.1f}°")

    st.markdown(
        f"""
        <div style='background: linear-gradient(90deg, rgba(15,23,42,0.9), rgba(192,38,211,0.2));
                    border: 2px solid #67e8f9; border-radius: 20px; padding: 22px; text-align:center; margin:25px 0;'>
            <p style='margin:0; font-size:1.45rem; font-weight:600; color:#67e8f9;'>
                📏 KHOẢNG CÁCH: <span style='color:#f0f9ff;'>{khoang_cach_str}</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    best_time_local, best_alt = best_observation_time(
        lua_chon, db_thien_the, observer, ts, horizon_hours=horizon_hours, step_minutes=plan_step
    )
    st.info(
        f"⏱️ Thời điểm đề xuất trong {horizon_hours} giờ tới: **{best_time_local.strftime('%H:%M')} (GMT+7)** "
        f"với độ cao cực đại khoảng **{best_alt:.1f}°**."
    )
    rs_status, rs_message = get_rise_set_info(lua_chon, latitude, longitude)
    if rs_status == "Sẵn sàng":
        st.caption(f"🌅 Giờ mọc/lặn tham khảo: {rs_message}")
    else:
        st.caption(f"🌅 Mọc/lặn ({rs_status}): {rs_message}")

    ten_ngan = lua_chon.split(" ", 1)[1].split(" (")[0] if "(" in lua_chon else lua_chon.split(" ", 1)[1]
    if alt > 0:
        st.success(
            f"**✅ CÓ THỂ QUAN SÁT NGAY!**  \nQuay kính hướng **{az:.0f}°** (Bắc = 0°), nâng góc **{alt:.0f}°**. "
            f"{ten_ngan} đang ở trên bầu trời Minh Đức!"
        )
    else:
        st.warning(
            f"**⏳ CHƯA LÊN CHÂN TRỜI**  \n{ten_ngan} đang ở dưới chân trời. "
            f"Hãy ưu tiên mốc giờ đề xuất phía trên để quan sát tốt hơn."
        )

    st.markdown(
        f"""
        <div class="fun-fact">
            <h4 style="margin:0 0 8px 0; color:#67e8f9;">🌟 FUN FACT</h4>
            <p style="margin:0; font-size:1.25rem; line-height:1.5;">{fun_facts.get(lua_chon, "Khám phá vũ trụ!")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

current_t = ts.now()
snapshot_rows = build_sky_snapshot_rows(db_thien_the, observer, current_t)
visible_count = sum(1 for row in snapshot_rows if row["visible"])
high_priority_count = sum(1 for row in snapshot_rows if row["Ưu tiên"] == "Cao")
metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric("Đang quan sát được", f"{visible_count}/{len(snapshot_rows)}")
with metric_col2:
    st.metric("Mục tiêu ưu tiên cao", high_priority_count)
with metric_col3:
    st.metric("Độ phủ dữ liệu", f"{len(snapshot_rows)} thiên thể")

tabs = st.tabs(["🌌 Bản đồ sao", "📅 Lập kế hoạch đêm", "📊 Tổng quan thông minh"])

with tabs[0]:
    st.caption("Di chuột vào các điểm để xem thông tin chi tiết • Xanh = Có thể quan sát")
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    fig, summary_rows = ve_ban_do_sao_tuong_tac(snapshot_rows, only_visible=only_visible)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    st.subheader("Lập kế hoạch theo thời gian")
    compare_targets = st.multiselect(
        "Chọn tối đa 4 thiên thể để so sánh độ cao",
        filtered_names,
        default=[lua_chon] if lua_chon in filtered_names else [],
    )
    compare_targets = compare_targets[:4]
    if compare_targets:
        time_axis = None
        timeline_fig = go.Figure()
        for target in compare_targets:
            timeline = build_timeline_for_object(
                db_thien_the[target], observer, ts, horizon_hours=horizon_hours, step_minutes=plan_step
            )
            if time_axis is None:
                time_axis = [p["time"] for p in timeline]
            timeline_fig.add_trace(
                go.Scatter(x=time_axis, y=[p["alt"] for p in timeline], mode="lines+markers", name=target)
            )
        timeline_fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
        timeline_fig.update_layout(
            title=f"Độ cao thiên thể theo thời gian ({horizon_hours}h tới)",
            xaxis_title="Thời gian (GMT+7)",
            yaxis_title="Altitude (°)",
            height=420,
        )
        st.plotly_chart(timeline_fig, use_container_width=True)
    else:
        st.info("Hãy chọn ít nhất 1 thiên thể để xem biểu đồ lập kế hoạch.")

    st.markdown("### Tonight Planner")
    planner_candidates = [name for name in db_thien_the if OBJECT_CATEGORIES.get(name) != "Thiên hà"]
    planner_rows = []
    for name in planner_candidates:
        score, max_alt, vis_pct, best_time = score_target_for_tonight(
            name, db_thien_the, observer, ts, horizon_hours=horizon_hours, step_minutes=plan_step
        )
        planner_rows.append(
            {
                "Mục tiêu": name,
                "Nhóm": OBJECT_CATEGORIES.get(name, "Khác"),
                "Điểm ưu tiên": score,
                "Độ cao cực đại (°)": max_alt,
                "Tỷ lệ nhìn thấy (%)": vis_pct,
                "Giờ nên ngắm (GMT+7)": best_time,
            }
        )
    planner_rows = sorted(planner_rows, key=lambda row: row["Điểm ưu tiên"], reverse=True)[:8]
    planner_df = pd.DataFrame(planner_rows)
    st.dataframe(planner_df, use_container_width=True, hide_index=True)
    st.download_button(
        label="⬇️ Tải kế hoạch Tonight Planner (CSV)",
        data=create_csv_bytes(planner_rows),
        file_name=f"tonight_planner_{datetime.now(LOCAL_TZ).strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        label="⬇️ Tải kế hoạch Tonight Planner (Excel)",
        data=create_excel_bytes(planner_df),
        file_name=f"tonight_planner_{datetime.now(LOCAL_TZ).strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with tabs[2]:
    st.subheader("Bảng tóm tắt quan sát nhanh")
    summary_rows = [{k: v for k, v in row.items() if k != "visible"} for row in snapshot_rows]
    if summary_rows:
        visible_count = len([row for row in summary_rows if row["Trạng thái"] == "Có thể quan sát"])
        top_targets = sorted(summary_rows, key=lambda row: row["Altitude (°)"], reverse=True)[:5]
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Thiên thể đang quan sát được", f"{visible_count}/{len(summary_rows)}")
        with col_b:
            st.metric("Mục tiêu đang lọc", len(filtered_names))
        summary_df = pd.DataFrame(summary_rows)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.download_button(
            label="⬇️ Tải bảng tổng quan (CSV)",
            data=create_csv_bytes(summary_rows),
            file_name=f"tong_quan_bau_troi_{datetime.now(LOCAL_TZ).strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
        st.download_button(
            label="⬇️ Tải bảng tổng quan (Excel)",
            data=create_excel_bytes(summary_df),
            file_name=f"tong_quan_bau_troi_{datetime.now(LOCAL_TZ).strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.markdown("**Top 5 mục tiêu nên ưu tiên lúc này:**")
        for idx, row in enumerate(top_targets, start=1):
            st.write(f"{idx}. {row['Thiên thể']} — Alt {row['Altitude (°)']}° ({row['Trạng thái']})")
        st.markdown("**Cửa sổ quan sát tiếp theo (mục đang chọn):**")
        start_dt, end_dt = next_visibility_window(
            db_thien_the[lua_chon], observer, ts, horizon_hours=horizon_hours, step_minutes=max(plan_step, 10)
        )
        if start_dt:
            start_str = start_dt.astimezone(LOCAL_TZ).strftime("%H:%M")
            end_str = end_dt.astimezone(LOCAL_TZ).strftime("%H:%M") if end_dt else "sau mốc dự báo"
            st.success(f"{lua_chon}: bắt đầu thấy từ **{start_str}**, kéo dài đến **{end_str}** (GMT+7).")
        else:
            st.warning(f"{lua_chon} chưa lên chân trời trong {horizon_hours} giờ tới.")
    else:
        st.warning("Không có dữ liệu tóm tắt.")

st.caption("✨ Sản phẩm của lớp 9.1 - Viết bằng Python với thư viện Skyfield và Streamlit")
