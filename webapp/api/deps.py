from __future__ import annotations

from fastapi import HTTPException, Request

from webapp.auth import validate_init_data


def get_repo(request: Request):
    """Get repository from app state."""
    return request.app.state.repo


def get_current_user_id(request: Request) -> int:
    """Extract and validate user from Telegram initData header."""
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    if not init_data:
        raise HTTPException(status_code=401, detail="Missing init data")

    bot_token = request.app.state.bot_token
    user = validate_init_data(init_data, bot_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid init data")

    return user["id"]
