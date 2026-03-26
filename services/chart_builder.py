from __future__ import annotations

import io

import plotly.graph_objects as go

from db.repository import CategoryTotal, DailyTotal
from services.reporter import CURRENCY_SYMBOLS, MONTH_NAMES_RU

# Modern color palette
COLORS = [
    "#6366F1",  # indigo
    "#F59E0B",  # amber
    "#EF4444",  # red
    "#10B981",  # emerald
    "#3B82F6",  # blue
    "#EC4899",  # pink
    "#8B5CF6",  # violet
    "#14B8A6",  # teal
    "#F97316",  # orange
    "#6B7280",  # gray
]

_LAYOUT_DEFAULTS = dict(
    font=dict(family="Arial, sans-serif", size=13),
    paper_bgcolor="#FAFAFA",
    plot_bgcolor="#FAFAFA",
    margin=dict(l=50, r=30, t=70, b=50),
)


def _to_png(fig: go.Figure) -> io.BytesIO:
    buf = io.BytesIO()
    fig.write_image(buf, format="png", scale=2)
    buf.seek(0)
    return buf


def build_pie_chart(
    categories: list[CategoryTotal], period_label: str, currency: str
) -> io.BytesIO:
    sym = CURRENCY_SYMBOLS.get(currency, currency)

    if not categories:
        fig = go.Figure()
        fig.add_annotation(text="Нет данных", showarrow=False, font=dict(size=20))
        fig.update_layout(**_LAYOUT_DEFAULTS, title=f"Расходы за {period_label}")
        return _to_png(fig)

    labels = [f"{c.icon} {c.name}" for c in categories]
    values = [c.total for c in categories]
    total = sum(values)

    # Custom text: amount + percentage
    text_info = [f"{v:,.0f} {sym}<br>({v/total*100:.1f}%)" for v in values]

    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            hole=0.45,  # donut chart — more modern
            marker=dict(colors=COLORS[:len(categories)], line=dict(color="#fff", width=2)),
            textinfo="text",
            text=text_info,
            textfont=dict(size=12),
            hovertemplate="%{label}: %{value:,.2f} " + sym + "<extra></extra>",
            pull=[0.03] * len(categories),  # slight pull for depth
        )
    ])

    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title=dict(text=f"📊 Расходы за {period_label}", font=dict(size=18)),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=12),
        ),
        annotations=[
            dict(
                text=f"<b>{total:,.0f}</b><br>{sym}",
                x=0.5, y=0.5,
                font=dict(size=20),
                showarrow=False,
            )
        ],
        width=900,
        height=550,
    )

    return _to_png(fig)


def build_bar_chart(
    daily_totals: list[DailyTotal], period_label: str, currency: str
) -> io.BytesIO:
    sym = CURRENCY_SYMBOLS.get(currency, currency)

    if not daily_totals:
        fig = go.Figure()
        fig.add_annotation(text="Нет данных", showarrow=False, font=dict(size=20))
        fig.update_layout(**_LAYOUT_DEFAULTS, title=f"Расходы по дням — {period_label}")
        return _to_png(fig)

    dates = [d.date for d in daily_totals]
    amounts = [d.total for d in daily_totals]
    total = sum(amounts)
    avg = total / len(amounts) if amounts else 0

    fig = go.Figure()

    # Main bars with gradient-like effect
    fig.add_trace(go.Bar(
        x=dates,
        y=amounts,
        marker=dict(
            color=amounts,
            colorscale=[[0, "#818CF8"], [1, "#4F46E5"]],
            line=dict(width=0),
            cornerradius=4,
        ),
        text=[f"{a:,.0f}" for a in amounts],
        textposition="outside",
        textfont=dict(size=10),
        hovertemplate="%{x}<br>%{y:,.2f} " + sym + "<extra></extra>",
    ))

    # Average line
    fig.add_hline(
        y=avg,
        line_dash="dash",
        line_color="#EF4444",
        line_width=1.5,
        annotation_text=f"Среднее: {avg:,.0f} {sym}",
        annotation_font=dict(color="#EF4444", size=11),
        annotation_position="top right",
    )

    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title=dict(text=f"📅 Расходы по дням — {period_label}", font=dict(size=18)),
        xaxis=dict(
            title="",
            tickformat="%d.%m",
            gridcolor="#E5E7EB",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title=f"Сумма ({sym})",
            gridcolor="#E5E7EB",
            zeroline=True,
            zerolinecolor="#D1D5DB",
        ),
        showlegend=False,
        bargap=0.2,
        width=900,
        height=500,
    )

    return _to_png(fig)


def build_comparison_chart(
    current_cats: list[CategoryTotal],
    previous_cats: list[CategoryTotal],
    current_label: str,
    previous_label: str,
    currency: str,
) -> io.BytesIO:
    """Side-by-side bar chart comparing two periods."""
    sym = CURRENCY_SYMBOLS.get(currency, currency)

    # Merge all category names
    all_names = list(dict.fromkeys(
        [c.name for c in current_cats] + [c.name for c in previous_cats]
    ))
    prev_map = {c.name: c.total for c in previous_cats}
    cur_map = {c.name: c.total for c in current_cats}

    labels = [n for n in all_names]
    prev_vals = [prev_map.get(n, 0) for n in all_names]
    cur_vals = [cur_map.get(n, 0) for n in all_names]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name=previous_label,
        x=labels, y=prev_vals,
        marker=dict(color="#94A3B8", cornerradius=4),
        text=[f"{v:,.0f}" for v in prev_vals],
        textposition="outside",
        textfont=dict(size=10),
    ))

    fig.add_trace(go.Bar(
        name=current_label,
        x=labels, y=cur_vals,
        marker=dict(color="#6366F1", cornerradius=4),
        text=[f"{v:,.0f}" for v in cur_vals],
        textposition="outside",
        textfont=dict(size=10),
    ))

    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title=dict(text=f"📊 {previous_label} → {current_label}", font=dict(size=18)),
        barmode="group",
        xaxis=dict(gridcolor="#E5E7EB", tickfont=dict(size=11)),
        yaxis=dict(title=f"Сумма ({sym})", gridcolor="#E5E7EB"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        bargap=0.25,
        bargroupgap=0.1,
        width=900,
        height=550,
    )

    return _to_png(fig)


def build_trend_chart(
    monthly_data: list[tuple[str, float]],
    currency: str,
    n_months: int,
) -> io.BytesIO:
    """Line chart showing spending trend over N months."""
    sym = CURRENCY_SYMBOLS.get(currency, currency)

    if not monthly_data:
        fig = go.Figure()
        fig.add_annotation(text="Нет данных", showarrow=False, font=dict(size=20))
        fig.update_layout(**_LAYOUT_DEFAULTS, title="Тренд расходов")
        return _to_png(fig)

    months = [d[0] for d in monthly_data]
    totals = [d[1] for d in monthly_data]

    # Pretty month labels
    month_labels = []
    for m in months:
        parts = m.split("-")
        month_num = int(parts[1])
        month_labels.append(f"{MONTH_NAMES_RU[month_num][:3]} {parts[0][2:]}")

    avg = sum(totals) / len(totals) if totals else 0

    fig = go.Figure()

    # Area fill under the line
    fig.add_trace(go.Scatter(
        x=month_labels, y=totals,
        mode="lines+markers+text",
        fill="tozeroy",
        fillcolor="rgba(99, 102, 241, 0.1)",
        line=dict(color="#6366F1", width=3, shape="spline"),
        marker=dict(size=10, color="#6366F1", line=dict(color="#fff", width=2)),
        text=[f"{t:,.0f}" for t in totals],
        textposition="top center",
        textfont=dict(size=11, color="#4F46E5"),
        hovertemplate="%{x}<br>%{y:,.2f} " + sym + "<extra></extra>",
    ))

    # Average line
    fig.add_hline(
        y=avg,
        line_dash="dash",
        line_color="#EF4444",
        line_width=1.5,
        annotation_text=f"Среднее: {avg:,.0f} {sym}",
        annotation_font=dict(color="#EF4444", size=11),
        annotation_position="top right",
    )

    # Delta annotation (first vs last)
    if len(totals) >= 2:
        delta = totals[-1] - totals[0]
        delta_pct = (delta / totals[0] * 100) if totals[0] else 0
        color = "#EF4444" if delta > 0 else "#10B981"
        arrow = "↑" if delta > 0 else "↓"
        fig.add_annotation(
            x=month_labels[-1], y=totals[-1],
            text=f"{arrow} {delta_pct:+.1f}%",
            showarrow=True,
            arrowhead=0,
            font=dict(size=14, color=color, family="Arial Black"),
            ax=40, ay=-40,
        )

    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title=dict(
            text=f"📈 Тренд расходов за {n_months} мес.",
            font=dict(size=18),
        ),
        xaxis=dict(gridcolor="#E5E7EB", tickfont=dict(size=11)),
        yaxis=dict(title=f"Сумма ({sym})", gridcolor="#E5E7EB"),
        showlegend=False,
        width=900,
        height=500,
    )

    return _to_png(fig)
