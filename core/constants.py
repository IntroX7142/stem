from datetime import timedelta, timezone

DEFAULT_LAT = 10.9500
DEFAULT_LON = 107.0100
LOCAL_TZ = timezone(timedelta(hours=7))
PROFILE_STORE = "observer_profiles.json"

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
