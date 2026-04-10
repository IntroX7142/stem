from datetime import datetime, timedelta, timezone
import time

import plotly.graph_objects as go
import streamlit as st
from skyfield.api import Star, Topos, load

# ====================== CẤU HÌNH VỊ TRÍ QUAN SÁT ======================
THCS_MINH_DUC = Topos("10.9500 N", "107.0100 E")
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


def ve_ban_do_sao_tuong_tac(db_thien_the, observer, ts, only_visible=False):
    fig = go.Figure()
    rows = []
    t = ts.now()
    for ten, obj in db_thien_the.items():
        alt, az, _ = compute_alt_az(obj, observer, t)
        visible = alt > 0
        if only_visible and not visible:
            continue
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
        rows.append(
            {
                "Thiên thể": ten,
                "Altitude (°)": round(alt, 1),
                "Azimuth (°)": round(az, 1),
                "Trạng thái": "Có thể quan sát" if visible else "Dưới chân trời",
                "Ưu tiên": "Cao" if alt > 30 else ("Trung bình" if alt > 10 else "Thấp"),
            }
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
    return fig, rows

# ====================== Giao diện ======================
def apply_modern_dark_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle at 30% 20%, #1a0f35 0%, #0a051f 35%, #0c0022 70%, #000011 100%);
        background-size: 250% 250%;
        animation: cosmic-drift 25s ease infinite;
        font-family: 'Inter', system-ui, sans-serif;
        color: #f0f9ff;
    }
    
    @keyframes cosmic-drift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Hiệu ứng sao lấp lánh nhẹ */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle, rgba(255,255,255,0.9) 1px, transparent 0);
        background-size: 80px 80px;
        animation: twinkle 8s linear infinite;
        opacity: 0.15;
        pointer-events: none;
        z-index: -1;
    }
    
    @keyframes twinkle {
        0%, 100% { opacity: 0.15; }
        50% { opacity: 0.35; }
    }
    
    h1 {
        font-size: 3.4rem !important;
        font-weight: 700;
        letter-spacing: -3px;
        background: linear-gradient(90deg, #67e8f9, #c026d3, #67e8f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(103,232,249,0.6);
    }
    
    .subtitle { font-size: 1.4rem; color: #94a3b8; text-align: center; font-weight: 500; }
    
    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(103, 232, 249, 0.3) !important;
        border-radius: 24px !important;
        padding: 28px 24px !important;
        box-shadow: 0 15px 35px -10px rgba(103, 232, 249, 0.4),
                    inset 0 2px 0 rgba(255,255,255,0.15);
    }
    
    [data-testid="stMetricValue"] { font-size: 3.2rem !important; color: #67e8f9 !important; text-shadow: 0 0 20px rgba(103,232,249,0.7); }
    
    .stButton > button {
        background: linear-gradient(90deg, #67e8f9, #c026d3) !important;
        color: #0a051f !important;
        font-size: 1.55rem !important;
        font-weight: 700;
        padding: 20px 50px !important;
        border-radius: 9999px !important;
        box-shadow: 0 15px 30px -8px rgba(103, 232, 249, 0.6);
        animation: buttonPulse 2s infinite ease-in-out;
    }
    
    @keyframes buttonPulse {
        0%, 100% { box-shadow: 0 15px 30px -8px rgba(103, 232, 249, 0.6); }
        50% { box-shadow: 0 20px 40px -8px rgba(192, 38, 211, 0.7); }
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.9) !important;
        border: 2px solid rgba(103, 232, 249, 0.5) !important;
        border-radius: 18px !important;
        color: #f0f9ff !important;
        font-size: 1.3rem !important;
    }
    
    /* Fun Fact Card */
    .fun-fact {
        background: linear-gradient(90deg, rgba(15,23,42,0.95), rgba(192,38,211,0.15));
        border: 2px solid #67e8f9;
        border-radius: 20px;
        padding: 20px 28px;
        box-shadow: 0 10px 30px -10px rgba(103,232,249,0.5);
        margin: 25px 0;
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
observer = earth + THCS_MINH_DUC

ctl_col1, ctl_col2, ctl_col3 = st.columns([2, 1, 1])
with ctl_col1:
    lua_chon = st.selectbox("🪐 CHỌN MỤC TIÊU CỦA BẠN:", list(db_thien_the.keys()), label_visibility="visible")
with ctl_col2:
    only_visible = st.toggle("Chỉ hiện mục đang nhìn thấy", value=False)
with ctl_col3:
    auto_refresh = st.toggle("Tự động cập nhật", value=False)

refresh_seconds = 20
if auto_refresh:
    refresh_seconds = st.slider("Chu kỳ làm mới (giây)", min_value=10, max_value=120, value=20, step=5)

if st.button("📍 BẮT ĐẦU DÒ TÌM & QUAN SÁT", use_container_width=True):
    try:
        alt, az, khoang_cach_str = tinh_toan_vi_tri(lua_chon, db_thien_the, observer, ts)
    except Exception:
        st.error("Không thể tính vị trí thiên thể lúc này. Vui lòng thử lại sau vài giây.")
        st.stop()

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

    best_time_local, best_alt = best_observation_time(lua_chon, db_thien_the, observer, ts)
    st.info(
        f"⏱️ Thời điểm đề xuất trong 12 giờ tới: **{best_time_local.strftime('%H:%M')} (GMT+7)** "
        f"với độ cao cực đại khoảng **{best_alt:.1f}°**."
    )

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

st.markdown("---")
st.subheader("🌌 BẢN ĐỒ SAO TƯƠNG TÁC TOÀN BẦU TRỜI")
st.caption("Di chuột vào các điểm để xem thông tin chi tiết • Xanh = Có thể quan sát")
fig, summary_rows = ve_ban_do_sao_tuong_tac(db_thien_the, observer, ts, only_visible=only_visible)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("📋 Bảng tóm tắt quan sát nhanh")
if summary_rows:
    st.dataframe(summary_rows, use_container_width=True, hide_index=True)
else:
    st.warning("Không có thiên thể nào đang ở trên bầu trời với bộ lọc hiện tại.")

if auto_refresh:
    st.caption(f"Tự động làm mới mỗi {refresh_seconds} giây.")
    time.sleep(refresh_seconds)
    st.rerun()

st.caption("✨ Sản phẩm của lớp 9.1 - Viết bằng Python với thư viện Skyfield và Streamlit")
