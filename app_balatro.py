import streamlit as st
from skyfield.api import load, Topos, Star
import plotly.graph_objects as go

# ==========================================
# 1. CẤU HÌNH TRANG VÀ GIAO DIỆN DARK NEON
# ==========================================
st.set_page_config(page_title="Radar Thiên Văn 9.1", page_icon="🛸")

# CSS tạo hiệu ứng Dark Neon (Cyberpunk Style)
st.markdown("""
<style>
    /* Nền tối đen */
    .stApp {
        background-color: #0b0c10;
        color: #66fcf1;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Hiệu ứng phát sáng cho tiêu đề (Neon Pink & Cyan) */
    h1 {
        color: #ff00ff !important;
        text-shadow: 0 0 10px #ff00ff, 0 0 20px #ff00ff, 0 0 40px #ff00ff;
        text-align: center;
        text-transform: uppercase;
    }
    h3 {
        color: #00ffcc !important;
        text-shadow: 0 0 5px #00ffcc;
    }

    /* Viền phát sáng cho các khối thông tin (Metrics) */
    div[data-testid="stMetric"] {
        background-color: rgba(31, 40, 51, 0.8);
        border: 2px solid #45a29e;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 0 15px #45a29e;
    }
    div[data-testid="stMetricValue"] {
        color: #ff00ff !important;
        text-shadow: 0 0 5px #ff00ff;
    }
    div[data-testid="stMetricLabel"] {
        color: #c5c6c7 !important;
    }

    /* Nút bấm Neon Xanh lá */
    .stButton>button {
        background-color: transparent;
        color: #39ff14;
        border: 2px solid #39ff14;
        box-shadow: 0 0 10px #39ff14;
        transition: 0.3s;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #39ff14;
        color: #000;
        box-shadow: 0 0 20px #39ff14, 0 0 40px #39ff14;
    }
    
    /* Footer Credit */
    .credit {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid #ff00ff;
        box-shadow: 0 -5px 15px rgba(255, 0, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. KHỞI TẠO DỮ LIỆU & BỘ SƯU TẬP THIÊN THỂ
# ==========================================
# Tối ưu: Dùng cache để không phải load lại file de421.bsp mỗi lần bấm nút
@st.cache_resource
def load_data():
    return load('de421.bsp')

planets = load_data()
earth = planets['earth']
THCS_MINH_DUC = Topos('10.9500 N', '107.0100 E')

# MỞ RỘNG DANH SÁCH THIÊN THỂ
db_thien_the = {
    # --- Hệ Mặt Trời ---
    "☀️ Mặt Trời": planets['sun'],
    "🌕 Mặt Trăng": planets['moon'],
    "🪐 Sao Thủy": planets['mercury'],
    "🪐 Sao Kim": planets['venus'],
    "🪐 Sao Hỏa": planets['mars'],
    "🪐 Sao Mộc": planets['jupiter barycenter'],
    "🪐 Sao Thổ": planets['saturn barycenter'],
    "🪐 Sao Thiên Vương": planets['uranus barycenter'],
    "🪐 Sao Hải Vương": planets['neptune barycenter'],
    
    # --- Những Ngôi Sao Sáng Nhất ---
    "⭐ Sao Thiên Lang (Sirius) - Sáng nhất bầu trời": Star(ra_hours=6.75, dec_degrees=-16.71),
    "⭐ Sao Chức Nữ (Vega) - Đại diện mùa hè": Star(ra_hours=18.61, dec_degrees=38.78),
    
    # --- Cụm Sao & Tinh Vân (Deep Sky) ---
    "✨ Cụm sao Tua Nắng (Pleiades/M45)": Star(ra_hours=3.78, dec_degrees=24.11),
    "✨ Chòm Thợ Săn (Orion)": Star(ra_hours=5.5, dec_degrees=0.0),
    "🌀 Tinh vân Orion (M42) - Nơi sinh ra các vì sao": Star(ra_hours=5.58, dec_degrees=-5.39),
    "🌀 Thiên hà Andromeda (M31)": Star(ra_hours=0.7, dec_degrees=41.2),
}

# Hàm tính toán (giữ nguyên logic gốc của bạn)
def tinh_toan_vi_tri(thien_the_chon):
    ts = load.timescale()
    t = ts.now() 
    nguoi_quan_sat = earth + THCS_MINH_DUC
    astrometric = nguoi_quan_sat.at(t).observe(db_thien_the[thien_the_chon])
    alt, az, distance = astrometric.apparent().altaz()
    dist_str = f"{distance.km:,.0f} km" if hasattr(distance, 'km') else "Hàng năm ánh sáng"
    return alt.degrees, az.degrees, dist_str

# ==========================================
# 3. LUỒNG CHƯƠNG TRÌNH CHÍNH (UI)
# ==========================================
st.title("🛰️ RA-ĐA KHÔNG GIAN")
st.markdown("<p style='text-align: center; color: #66fcf1;'>Tọa độ quét: THCS Minh Đức, Đồng Nai</p>", unsafe_allow_html=True)

lua_chon = st.selectbox("🎯 NHẬP MỤC TIÊU:", list(db_thien_the.keys()))

if st.button("🚀 KÍCH HOẠT QUÉT"):
    alt, az, khoang_cach_str = tinh_toan_vi_tri(lua_chon)
    ten_ngan = lua_chon.split(" ", 1)[1]
    
    st.write("---")
    
    # Hiển thị thông số
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("GÓC CAO (ALT)", f"{alt:.1f}°")
    with col2: st.metric("HƯỚNG (AZ)", f"{az:.1f}°")
    with col3: st.metric("KHOẢNG CÁCH", khoang_cach_str)

    # --- RADAR THEO PHONG CÁCH NEON ---
    st.markdown("<h3 style='text-align:center; margin-top:30px;'>📡 MÀN HÌNH ĐỊNH VỊ CHÍNH</h3>", unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[alt if alt > 0 else 0], 
        theta=[az],
        mode='markers+text',
        marker=dict(size=20, color='#ff00ff', symbol='cross'), # Marker hình chữ thập màu hồng Neon
        text=[ten_ngan],
        textposition="top center",
        textfont=dict(color="#39ff14", size=16, family="Courier New") # Chữ nhãn màu xanh lá Neon
    ))

    # Tùy chỉnh lưới Radar cho giống màn hình thiết bị viễn tưởng
    fig.update_layout(
        polar=dict(
            bgcolor="#050510",
            angularaxis=dict(direction="clockwise", period=360, color="#45a29e", gridcolor="#1f2833"),
            radialaxis=dict(range=[0, 90], color="#45a29e", gridcolor="#1f2833", showticklabels=False)
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Thông báo trạng thái
    if alt > 0:
        st.success(f"🟢 ĐÃ KHÓA MỤC TIÊU: {ten_ngan} đang hiển thị trên ra-đa.")
    else:
        st.error(f"🔴 MẤT TÍN HIỆU: {ten_ngan} hiện đang nằm dưới đường chân trời.")

# ==========================================
# 4. CREDIT SẢN PHẨM
# ==========================================
st.markdown("""
<div class='credit'>
    <span style='color: #66fcf1; font-size: 1.2rem;'>💻 Sản phẩm của <b>LỚP 9.1</b></span><br>
    <span style='color: #ff00ff; font-size: 0.9rem;'><i>Viết bằng Python cho dự án STEM</i> 🐍</span>
</div>
""", unsafe_allow_html=True)
