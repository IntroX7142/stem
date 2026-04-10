import streamlit as st
from skyfield.api import load, Topos, Star
import plotly.graph_objects as go
import math

# ==========================================
# 1. CẤU HÌNH CƠ BẢN & GIAO DIỆN STREAMLIT
# ==========================================
st.set_page_config(page_title="Radar Thiên Văn 9.1", page_icon="🔭", layout="centered")

# ==========================================
# 2. DỮ LIỆU THIÊN VĂN (BACKEND)
# ==========================================
@st.cache_resource
def load_astronomy_data():
    """Tải dữ liệu NASA một lần duy nhất để ứng dụng chạy nhanh hơn"""
    planets = load('de421.bsp')
    return planets

planets = load_astronomy_data()
earth = planets['earth']
THCS_MINH_DUC = Topos('10.9500 N', '107.0100 E')

# Từ điển thiên thể (Đã chuẩn hóa Tiếng Việt có dấu)
db_thien_the = {
    "☀️ Mặt Trời": planets['sun'],
    "🌕 Mặt Trăng": planets['moon'],
    "🪐 Sao Thủy": planets['mercury'],
    "🪐 Sao Kim": planets['venus'],
    "🪐 Sao Hỏa": planets['mars'],
    "🪐 Sao Mộc": planets['jupiter barycenter'],
    "🪐 Sao Thổ": planets['saturn barycenter'],
    "✨ Chòm Thợ Săn (Orion)": Star(ra_hours=5.5, dec_degrees=0.0),
    "🌀 Thiên hà Andromeda": Star(ra_hours=0.7, dec_degrees=41.2),
}

def tinh_toan_vi_tri(thien_the_chon):
    ts = load.timescale()
    t = ts.now() 
    nguoi_quan_sat = earth + THCS_MINH_DUC
    doi_tuong = db_thien_the[thien_the_chon]
    
    astrometric = nguoi_quan_sat.at(t).observe(doi_tuong)
    alt, az, distance = astrometric.apparent().altaz()
    
    dist_str = f"{distance.km:,.0f} km" if hasattr(distance, 'km') else "Ngoài Hệ Mặt Trời"
    return alt.degrees, az.degrees, dist_str

# ==========================================
# 3. CSS TÙY CHỈNH (STYLE BALATRO GỌN GÀNG)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    /* Nền vũ trụ chuyển màu nhẹ nhàng */
    .stApp {
        background: linear-gradient(135deg, #1a0b2e 0%, #4b1d52 50%, #1a0b2e 100%);
        background-size: 200% 200%;
        animation: gradient-swirl 10s ease infinite;
        font-family: 'VT323', monospace;
        color: #f1faee;
    }
    @keyframes gradient-swirl {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Ép tất cả chữ dùng font Pixel */
    * { font-family: 'VT323', monospace !important; }

    /* Tiêu đề chính */
    h1 {
        color: #fee440;
        text-shadow: 4px 4px 0px #c1121f;
        text-align: center;
        font-size: 3.5rem !important;
        margin-bottom: 0px !important;
    }

    /* Khối thẻ bài (Metrics) */
    div[data-testid="stMetric"] {
        background-color: rgba(20, 10, 40, 0.85);
        border: 3px solid #fee440;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 4px 4px 0px #c1121f;
        text-align: center;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        color: #ffffff !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1.5rem !important;
        color: #fee440 !important;
    }

    /* Nút bấm */
    .stButton>button {
        background-color: #c1121f;
        color: white;
        font-size: 1.8rem !important;
        border: 3px solid #fee440;
        border-radius: 8px;
        width: 100%;
        box-shadow: 4px 4px 0px #000;
        transition: 0.1s;
    }
    .stButton>button:active {
        box-shadow: 0px 0px 0px #000;
        transform: translateY(4px);
    }
    
    /* Footer Credit */
    .credit-footer {
        text-align: center;
        color: #a8dadc;
        font-size: 1.5rem;
        margin-top: 50px;
        border-top: 2px dashed #fee440;
        padding-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. GIAO DIỆN NGƯỜI DÙNG (FRONTEND)
# ==========================================
st.title("🔭 TRẠM RA-ĐA THIÊN VĂN")
st.markdown("<p style='text-align: center; font-size: 1.5rem; color: #a8dadc;'>Định vị bầu trời tại: THCS Minh Đức, Đồng Nai</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Khung chọn
lua_chon = st.selectbox("🪐 CHỌN MỤC TIÊU:", list(db_thien_the.keys()))

if st.button("📍 KÍCH HOẠT QUÉT RA-ĐA"):
    alt, az, khoang_cach_str = tinh_toan_vi_tri(lua_chon)
    ten_ngan = lua_chon.split(" ", 1)[1] # Lấy tên bỏ icon
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hiển thị 3 khối thông tin cạnh nhau cho gọn
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("ĐỘ CAO", f"{alt:.1f}°")
    with col2: st.metric("PHƯƠNG VỊ", f"{az:.1f}°")
    with col3: st.metric("KHOẢNG CÁCH", khoang_cach_str)

    # Biểu đồ Radar Plotly (Đã dọn dẹp sạch sẽ)
    st.markdown("<h3 style='text-align:center; color:#fee440; margin-top:20px;'>🛰️ MÀN HÌNH ĐỊNH VỊ</h3>", unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[alt if alt > 0 else 0], 
        theta=[az],
        mode='markers+text',
        marker=dict(size=25, color='#fee440', symbol='star'),
        text=[ten_ngan],
        textposition="bottom center",
        textfont=dict(family="VT323", size=20, color="white")
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0, 0, 0, 0.4)",
            angularaxis=dict(direction="clockwise", period=360, color="#a8dadc", tickfont=dict(size=15)),
            radialaxis=dict(range=[0, 90], color="#a8dadc", showticklabels=False)
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=20),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Kết luận hướng dẫn
    if alt > 0:
        st.success(f"**THÀNH CÔNG:** {ten_ngan} đang nằm trên bầu trời! Hãy quay kính hướng **{az:.0f}°** và nâng góc **{alt:.0f}°**.")
    else:
        st.error(f"**CẢNH BÁO:** {ten_ngan} đang nằm dưới đường chân trời. Không thể quan sát lúc này.")

# ==========================================
# 5. CREDIT LỚP 9.1
# ==========================================
st.markdown("""
<div class='credit-footer'>
    Coded with ❤️ by <b>Lớp 9.1</b><br>
    <i>Sản phẩm dự thi STEM - Viết bằng Python</i> 🐍
</div>
""", unsafe_allow_html=True)
