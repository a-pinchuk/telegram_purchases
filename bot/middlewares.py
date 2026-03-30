from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from bot.config import Settings


class AccessMiddleware(BaseMiddleware):
    """Allow updates only from authorized users/chats."""

    def __init__(self, settings: Settings) -> None:
        self._allowed_users = settings.allowed_user_ids
        self._allowed_chat_id = settings.allowed_chat_id

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Update):
            user = None
            chat = None

            if event.message:
                chat = event.message.chat
                user = event.message.from_user
            elif event.callback_query and event.callback_query.message:
                chat = event.callback_query.message.chat
                user = event.callback_query.from_user

            # Private chat: check user whitelist (if configured)
            if chat and chat.type == "private":
                if self._allowed_users and user and user.id not in self._allowed_users:
                    return None

            # Group/supergroup chat: check chat whitelist (if configured)
            elif chat and chat.type in ("group", "supergroup"):
                if self._allowed_chat_id and chat.id != self._allowed_chat_id:
                    return None
                # Also check user whitelist in groups
                if self._allowed_users and user and user.id not in self._allowed_users:
                    return None

        return await handler(event, data)
