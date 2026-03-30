from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from webapp.api.analytics import router as analytics_router
from webapp.api.categories import router as categories_router
from webapp.api.expenses import router as expenses_router

STATIC_DIR = Path(__file__).parent.parent / "frontend" / "dist"


def create_app() -> FastAPI:
    app = FastAPI(title="Expense Tracker", docs_url="/api/docs", openapi_url="/api/openapi.json")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
    app.include_router(expenses_router, prefix="/api/expenses", tags=["expenses"])
    app.include_router(categories_router, prefix="/api/categories", tags=["categories"])

    # Serve frontend static files if built
    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

    return app
