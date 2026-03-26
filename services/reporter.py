from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from db.repository import CategoryTotal, Repository

CURRENCY_SYMBOLS = {
    "EUR": "€",
    "RUB": "₽",
    "PLN": "zł",
    "USD": "$",
    "GBP": "£",
    "CZK": "Kč",
}

MONTH_NAMES_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}


@dataclass
class PeriodRange:
    start: str  # ISO date
    end: str    # ISO date
    label: str  # Human-readable


@dataclass
class ReportData:
    period: PeriodRange
    currency: str
    categories: list[CategoryTotal]
    total: float
    count: int
    average: float


def parse_period(period_str: str | None) -> PeriodRange:
    """Parse period string into a date range."""
    today = date.today()

    if not period_str or period_str == "month":
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end = today.replace(month=today.month + 1, day=1)
        label = f"{MONTH_NAMES_RU[today.month]} {today.year}"

    elif period_str == "week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=7)
        label = f"Неделя {start.strftime('%d.%m')}–{(end - timedelta(days=1)).strftime('%d.%m')}"

    elif period_str == "year":
        start = today.replace(month=1, day=1)
        end = today.replace(year=today.year + 1, month=1, day=1)
        label = str(today.year)

    elif "-" in period_str:
        # "2026-03" or "2026-03-15"
        parts = period_str.split("-")
        if len(parts) == 2:
            year, month = int(parts[0]), int(parts[1])
            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1)
            else:
                end = date(year, month + 1, 1)
            label = f"{MONTH_NAMES_RU[month]} {year}"
        else:
            d = date.fromisoformat(period_str)
            start = d
            end = d + timedelta(days=1)
            label = d.strftime("%d.%m.%Y")
    else:
        # Fallback to current month
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end = today.replace(month=today.month + 1, day=1)
        label = f"{MONTH_NAMES_RU[today.month]} {today.year}"

    return PeriodRange(
        start=start.isoformat(),
        end=end.isoformat(),
        label=label,
    )


def get_previous_period(period: PeriodRange) -> PeriodRange:
    """Get the equivalent previous period for comparison."""
    start = date.fromisoformat(period.start)
    end = date.fromisoformat(period.end)
    duration = end - start

    prev_end = start
    prev_start = prev_end - duration

    # Determine label
    if duration.days >= 28 and duration.days <= 31:
        label = f"{MONTH_NAMES_RU[prev_start.month]} {prev_start.year}"
    elif duration.days == 7:
        label = f"Неделя {prev_start.strftime('%d.%m')}–{(prev_end - timedelta(days=1)).strftime('%d.%m')}"
    elif duration.days >= 365:
        label = str(prev_start.year)
    else:
        label = f"{prev_start.strftime('%d.%m')}–{(prev_end - timedelta(days=1)).strftime('%d.%m')}"

    return PeriodRange(start=prev_start.isoformat(), end=prev_end.isoformat(), label=label)


async def build_report(
    repo: Repository, user_id: int, period: PeriodRange, currency: str
) -> ReportData:
    categories = await repo.get_category_totals(user_id, period.start, period.end, currency)
    expenses = await repo.get_expenses(user_id, period.start, period.end, currency)
    total = sum(c.total for c in categories)
    count = len(expenses)
    average = total / count if count else 0

    return ReportData(
        period=period,
        currency=currency,
        categories=categories,
        total=total,
        count=count,
        average=average,
    )


def format_report(report: ReportData) -> str:
    sym = CURRENCY_SYMBOLS.get(report.currency, report.currency)
    lines = [f"📊 <b>Отчёт за {report.period.label}</b> ({sym})\n"]

    if not report.categories:
        lines.append("Нет расходов за этот период.")
        return "\n".join(lines)

    # Find max name length for alignment
    for cat in report.categories:
        amount_str = f"{cat.total:,.2f} {sym}"
        lines.append(f"{cat.icon} {cat.name}: <b>{amount_str}</b> ({cat.percentage:.0f}%) — {cat.count} шт.")

    lines.append("")
    lines.append(f"💰 Итого: <b>{report.total:,.2f} {sym}</b>")
    lines.append(f"📝 Записей: {report.count}")
    lines.append(f"📈 Средний чек: {report.average:,.2f} {sym}")

    return "\n".join(lines)


def format_comparison(current: ReportData, previous: ReportData) -> str:
    sym = CURRENCY_SYMBOLS.get(current.currency, current.currency)
    lines = [f"📊 <b>Сравнение: {previous.period.label} → {current.period.label}</b> ({sym})\n"]

    # Build a map of previous categories
    prev_map: dict[str, CategoryTotal] = {c.name: c for c in previous.categories}

    all_names = list(dict.fromkeys(
        [c.name for c in current.categories] + [c.name for c in previous.categories]
    ))

    for name in all_names:
        cur_cat = next((c for c in current.categories if c.name == name), None)
        prev_cat = prev_map.get(name)

        cur_total = cur_cat.total if cur_cat else 0
        prev_total = prev_cat.total if prev_cat else 0
        icon = (cur_cat.icon if cur_cat else prev_cat.icon) if (cur_cat or prev_cat) else "📦"

        if prev_total > 0:
            delta_pct = (cur_total - prev_total) / prev_total * 100
            arrow = "↑" if delta_pct > 0 else "↓" if delta_pct < 0 else "→"
            delta_str = f"{delta_pct:+.0f}% {arrow}"
        elif cur_total > 0:
            delta_str = "новая ↑"
        else:
            delta_str = "—"

        lines.append(f"{icon} {name}: {prev_total:,.2f} → <b>{cur_total:,.2f}</b> {sym} ({delta_str})")

    lines.append("")
    prev_t = previous.total
    cur_t = current.total
    if prev_t > 0:
        total_delta = (cur_t - prev_t) / prev_t * 100
        arrow = "↑" if total_delta > 0 else "↓" if total_delta < 0 else "→"
        lines.append(f"💰 Итого: {prev_t:,.2f} → <b>{cur_t:,.2f}</b> {sym} ({total_delta:+.0f}% {arrow})")
    else:
        lines.append(f"💰 Итого: 0 → <b>{cur_t:,.2f}</b> {sym}")

    return "\n".join(lines)


def format_trend(monthly_data: list[tuple[str, float]], currency: str, n_months: int) -> str:
    """Format a text summary of monthly spending trend."""
    sym = CURRENCY_SYMBOLS.get(currency, currency)
    lines = [f"📈 <b>Тренд расходов за {n_months} мес.</b> ({sym})\n"]

    if not monthly_data:
        lines.append("Нет данных за этот период.")
        return "\n".join(lines)

    total = 0.0
    for month_str, amount in monthly_data:
        parts = month_str.split("-")
        month_num = int(parts[1])
        year = parts[0]
        label = f"{MONTH_NAMES_RU[month_num]} {year}"
        total += amount
        lines.append(f"  {label}: <b>{amount:,.2f} {sym}</b>")

    avg = total / len(monthly_data)
    lines.append("")
    lines.append(f"💰 Всего: <b>{total:,.2f} {sym}</b>")
    lines.append(f"📊 Среднее в месяц: {avg:,.2f} {sym}")

    # Growth from first to last
    if len(monthly_data) >= 2:
        first = monthly_data[0][1]
        last = monthly_data[-1][1]
        if first > 0:
            delta = (last - first) / first * 100
            arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            lines.append(f"📉 Динамика: {delta:+.1f}% {arrow}")

    return "\n".join(lines)
