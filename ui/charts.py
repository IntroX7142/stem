import plotly.graph_objects as go

from data.catalog import FUN_FACTS


def sky_map_figure(rows, only_visible=False):
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
        fact = FUN_FACTS.get(ten, "Khám phá vũ trụ!")[:80] + "..."
        hover_text = (
            f"<b>{ten}</b><br>Độ cao: <b>{alt:.1f}°</b><br>Phương vị: <b>{az:.1f}°</b><br>"
            f"Trạng thái: {'<span style=\"color:#67e8f9\">VISIBLE</span>' if visible else 'Dưới chân trời'}<br>Fun fact: {fact}"
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
    fig.add_hline(y=0, line_dash="dash", line_color="#f1faee", line_width=2)
    fig.update_layout(
        title="🌌 BẢN ĐỒ SAO TƯƠNG TÁC",
        xaxis=dict(title="Phương vị (Azimuth °)", range=[0, 360]),
        yaxis=dict(title="Độ cao (Altitude °)", range=[-15, 90]),
        plot_bgcolor="rgba(10, 5, 31, 0.85)",
        paper_bgcolor="rgba(10, 5, 31, 0)",
        height=520,
        margin=dict(l=50, r=30, t=70, b=50),
        font=dict(family="Inter", color="#f0f9ff", size=14),
    )
    return fig, filtered_rows
