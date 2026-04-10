from skyfield.api import Star


def build_celestial_db(planets):
    return {
        "☀️ MẶT TRỜI": planets["sun"],
        "🌕 MẶT TRĂNG": planets["moon"],
        "🪐 Sao Thủy (Mercury)": planets["mercury"],
        "🪐 Sao Kim (Venus)": planets["venus"],
        "🪐 Sao Hỏa (Mars)": planets["mars"],
        "🪐 Sao Mộc (Jupiter)": planets["jupiter barycenter"],
        "🪐 Sao Thổ (Saturn)": planets["saturn barycenter"],
        "🪐 Sao Thiên Vương (Uranus)": planets["uranus barycenter"],
        "🪐 Sao Hải Vương (Neptune)": planets["neptune barycenter"],
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
        "🌀 Thiên hà Andromeda (M31)": Star(ra_hours=0.7, dec_degrees=41.2),
        "🌀 Tâm Ngân Hà (Milky Way Center)": Star(ra_hours=17.75, dec_degrees=-29.0),
    }


FUN_FACTS = {
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
    "⭐️ Sao Sirius": "Sirius là sao sáng nhất bầu trời đêm, cách chúng ta chỉ 8.6 năm ánh sáng.",
    "⭐️ Sao Betelgeuse": "Betelgeuse là sao khổng lồ đỏ trong Orion, nếu đặt ở vị trí Mặt Trời thì nó sẽ nuốt chửng cả sao Thủy đến sao Hỏa!",
    "⭐️ Sao Vega": "Vega từng là Sao Bắc Cực cách đây 12.000 năm và sẽ lại là Sao Bắc Cực trong tương lai.",
    "🌀 Thiên hà Andromeda (M31)": "Andromeda là thiên hà lớn nhất láng giềng, cách 2.5 triệu năm ánh sáng và đang lao về phía Ngân Hà!",
    "🌀 Tâm Ngân Hà (Milky Way Center)": "Trung tâm Ngân Hà chứa hố đen siêu nặng Sagittarius A* với khối lượng bằng 4 triệu Mặt Trời.",
}
