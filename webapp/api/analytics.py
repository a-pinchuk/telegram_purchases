from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from db.repository import Repository
from services.reporter import get_previous_period, parse_period
from webapp.api.deps import get_current_user_id, get_repo

router = APIRouter()


@router.get("/summary")
async def get_summary(
    period: str = Query("month"),
    currency: str = Query("EUR"),
    user_id: int = Depends(get_current_user_id),
    repo: Repository = Depends(get_repo),
):
    """Dashboard summary: total, count, average, delta vs previous period."""
    p = parse_period(period)

    # Show all users' data (shared family tracker)
    categories = await repo.get_category_totals(None, p.start, p.end, currency)
    expenses = await repo.get_expenses(None, p.start, p.end, currency)
    total = sum(c.total for c in categories)
    count = len(expenses)
    average = total / count if count else 0

    prev_p = get_previous_period(p)
    prev_categories = await repo.get_category_totals(None, prev_p.start, prev_p.end, currency)
    prev_total = sum(c.total for c in prev_categories)
    delta_pct = ((total - prev_total) / prev_total * 100) if prev_total else 0

    return {
        "period_label": p.label,
        "total": round(total, 2),
        "count": count,
        "average": round(average, 2),
        "prev_total": round(prev_total, 2),
        "delta_pct": round(delta_pct, 1),
        "currency": currency,
    }


@router.get("/categories")
async def get_category_totals(
    period: str = Query("month"),
    currency: str = Query("EUR"),
    user_id: int = Depends(get_current_user_id),
    repo: Repository = Depends(get_repo),
):
    """Category breakdown for charts."""
    p = parse_period(period)
    categories = await repo.get_category_totals(None, p.start, p.end, currency)
    return [
        {
            "name": c.name,
            "icon": c.icon,
            "total": round(c.total, 2),
            "count": c.count,
            "percentage": round(c.percentage, 1),
        }
        for c in categories
    ]


@router.get("/daily")
async def get_daily_totals(
    period: str = Query("month"),
    currency: str = Query("EUR"),
    user_id: int = Depends(get_current_user_id),
    repo: Repository = Depends(get_repo),
):
    """Daily totals for bar chart."""
    p = parse_period(period)
    daily = await repo.get_daily_totals(None, p.start, p.end, currency)
    return [{"date": d.date, "total": round(d.total, 2)} for d in daily]


@router.get("/monthly")
async def get_monthly_totals(
    months: int = Query(6, ge=2, le=24),
    currency: str = Query("EUR"),
    user_id: int = Depends(get_current_user_id),
    repo: Repository = Depends(get_repo),
):
    """Monthly totals for trend chart."""
    today = date.today()
    start_month = today.month - months
    start_year = today.year
    while start_month <= 0:
        start_month += 12
        start_year -= 1
    start = date(start_year, start_month, 1).isoformat()
    end_month = today.month + 1
    end_year = today.year
    if end_month > 12:
        end_month = 1
        end_year += 1
    end = date(end_year, end_month, 1).isoformat()

    monthly = await repo.get_monthly_totals(None, start, end, currency)
    return [{"month": m[0], "total": round(m[1], 2)} for m in monthly]


@router.get("/weekday")
async def get_weekday_totals(
    period: str = Query("month"),
    currency: str = Query("EUR"),
    user_id: int = Depends(get_current_user_id),
    repo: Repository = Depends(get_repo),
):
    """Spending by day of week for heatmap."""
    p = parse_period(period)
    expenses = await repo.get_expenses(None, p.start, p.end, currency)

    weekday_totals = [0.0] * 7
    weekday_counts = [0] * 7
    for exp in expenses:
        d = date.fromisoformat(exp.created_at[:10])
        wd = d.weekday()
        weekday_totals[wd] += exp.amount
        weekday_counts[wd] += 1

    days_ru = ["\u041f\u043d", "\u0412\u0442", "\u0421\u0440", "\u0427\u0442", "\u041f\u0442", "\u0421\u0431", "\u0412\u0441"]
    return [
        {"day": days_ru[i], "day_index": i, "total": round(weekday_totals[i], 2), "count": weekday_counts[i]}
        for i in range(7)
    ]


@router.get("/currencies")
async def get_currencies(
    period: str = Query("month"),
    user_id: int = Depends(get_current_user_id),
    repo: Repository = Depends(get_repo),
):
    """List currencies used in a period."""
    p = parse_period(period)
    currencies = await repo.get_currencies_used(None, p.start, p.end)
    if not currencies:
        default = await repo.get_user_currency(user_id)
        currencies = [default]
    return currencies
