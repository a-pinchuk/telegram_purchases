from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def category_keyboard(
    categories: list[tuple[int, str, str]], expense_id: int
) -> InlineKeyboardMarkup:
    """Build inline keyboard for category selection."""
    buttons = []
    for cat_id, name, icon in categories:
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {name}",
                callback_data=f"setcat:{expense_id}:{cat_id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def expense_actions_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    """Inline buttons shown after recording an expense."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📂 Категория", callback_data=f"chcat:{expense_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"del:{expense_id}"),
        ]
    ])


def confirm_delete_keyboard(expense_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirmdel:{expense_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
        ]
    ])
