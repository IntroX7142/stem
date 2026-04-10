import streamlit as st


def apply_modern_dark_theme():
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background: radial-gradient(circle at 20% -10%, #18223d 0%, #0d1428 45%, #090f1d 100%); font-family: 'Inter', system-ui, sans-serif; color: #e6edf7; }
    .block-container { padding-top: 2rem; max-width: 1200px; }
    h1 { font-size: 2.6rem !important; font-weight: 700; letter-spacing: -1px; color: #dbeafe !important; text-shadow: none; }
    .subtitle { font-size: 1rem; color: #9fb0cc; text-align: center; font-weight: 500; margin-top: -10px; margin-bottom: 8px; }
    .section-card { background: linear-gradient(180deg, rgba(20, 30, 52, 0.85) 0%, rgba(12, 20, 38, 0.9) 100%); border: 1px solid rgba(125, 160, 220, 0.22); border-radius: 16px; padding: 14px 18px; margin: 8px 0 16px; }
    [data-testid="stMetric"] { background: rgba(16, 26, 44, 0.75) !important; border: 1px solid rgba(125, 160, 220, 0.3) !important; border-radius: 16px !important; padding: 18px !important; box-shadow: none !important; }
    [data-testid="stMetricLabel"] { color: #9fb0cc !important; }
    [data-testid="stMetricValue"] { font-size: 2.1rem !important; color: #7dd3fc !important; }
    .stButton > button { background: #38bdf8 !important; color: #06101f !important; font-size: 1rem !important; font-weight: 700 !important; border-radius: 12px !important; border: none !important; padding: 0.65rem 1rem !important; }
    .stButton > button:hover { background: #0ea5e9 !important; color: #f8fbff !important; }
    .stSelectbox div[data-baseweb="select"], div[data-baseweb="input"], div[data-baseweb="base-input"] { background-color: rgba(11, 20, 37, 0.95) !important; border: 1px solid rgba(125, 160, 220, 0.35) !important; border-radius: 12px !important; color: #e6edf7 !important; }
    .fun-fact { background: rgba(12, 22, 39, 0.85); border: 1px solid rgba(125, 160, 220, 0.35); border-radius: 14px; padding: 16px 18px; margin: 16px 0 8px; }
    [data-testid="stDataFrame"] { border: 1px solid rgba(125, 160, 220, 0.25); border-radius: 12px; }
    </style>
    """,
        unsafe_allow_html=True,
    )
