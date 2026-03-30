from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from db.repository import Repository
from services.reporter import parse_period
from webapp.api.deps import get_current_user_id, get_repo

router = APIRouter()


@router.get("/")
async def list_expenses(
    period: str = Query("month"),
    currency: str | None = Query(None),
    category: str | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_current_user_id),
    repo: Repository = Depends(get_repo),
):
    """List expenses with filters. Shows all users' data (shared tracker)."""
    p = parse_period(period)
    # user_id=None to show all users' expenses
    expenses = await repo.get_expenses(None, p.start, p.end, currency)

    if category:
        expenses = [e for e in expenses if e.category_name == category]
    if search:
        q = search.lower()
        expenses = [e for e in expenses if q in (e.description or "").lower()]

    total_count = len(expenses)
    expenses = expenses[offset : offset + limit]

    return {
        "items": [
            {
                "id": e.id,
                "amount": e.amount,
                "currency": e.currency,
                "description": e.description,
                "category_name": e.category_name,
                "category_icon": e.category_icon,
                "store": e.store,
                "created_at": e.created_at,
            }
            for e in expenses
        ],
        "total_count": total_count,
        "period_label": p.label,
    }
