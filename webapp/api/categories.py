from __future__ import annotations

from fastapi import APIRouter, Depends

from db.repository import Repository
from webapp.api.deps import get_repo

router = APIRouter()


@router.get("/")
async def list_categories(repo: Repository = Depends(get_repo)):
    """List all categories."""
    cats = await repo.get_categories()
    return [{"id": c[0], "name": c[1], "icon": c[2]} for c in cats]
