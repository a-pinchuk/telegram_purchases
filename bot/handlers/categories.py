from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import category_keyboard
from db.repository import Repository

router = Router()


@router.message(Command("categories"))
async def cmd_categories(message: Message, repo: Repository) -> None:
    categories = await repo.get_categories()
    if not categories:
        await message.answer("Категории пока не заданы.")
        return

    lines = ["📋 <b>Категории:</b>\n"]
    for _, name, icon in categories:
        lines.append(f"  {icon} {name}")

    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("addstore"))
async def cmd_addstore(message: Message, repo: Repository) -> None:
    """Usage: /addstore lidl Продукты"""
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "Использование: <code>/addstore магазин Категория</code>\n"
            "Пример: <code>/addstore lidl Продукты</code>",
            parse_mode="HTML",
        )
        return

    pattern = parts[1].lower().strip()
    category_name = parts[2].strip()

    cat_id = await repo.get_category_id_by_name(category_name)
    if not cat_id:
        categories = await repo.get_categories()
        names = ", ".join(f"<b>{name}</b>" for _, name, _ in categories)
        await message.answer(f"Категория не найдена. Доступные: {names}", parse_mode="HTML")
        return

    await repo.add_store_mapping(pattern, cat_id, source="manual")
    await message.answer(f"✅ <b>{pattern}</b> → {category_name}", parse_mode="HTML")


@router.message(Command("currency"))
async def cmd_currency(message: Message, repo: Repository) -> None:
    user = message.from_user
    if not user:
        return

    args = (message.text or "").split()
    if len(args) < 2:
        current = await repo.get_user_currency(user.id)
        await message.answer(
            f"Текущая валюта: <b>{current}</b>\n"
            "Сменить: <code>/currency EUR</code>",
            parse_mode="HTML",
        )
        return

    new_currency = args[1].upper().strip()
    await repo.set_user_currency(user.id, new_currency)
    await message.answer(f"✅ Валюта по умолчанию: <b>{new_currency}</b>", parse_mode="HTML")


# ── Callback: change category on existing expense ──

@router.callback_query(F.data.startswith("chcat:"))
async def cb_change_category(callback: CallbackQuery, repo: Repository) -> None:
    expense_id = int(callback.data.split(":")[1])
    categories = await repo.get_categories()
    kb = category_keyboard(categories, expense_id)
    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("setcat:"))
async def cb_set_category(callback: CallbackQuery, repo: Repository) -> None:
    _, expense_id_str, cat_id_str = callback.data.split(":")
    expense_id = int(expense_id_str)
    cat_id = int(cat_id_str)

    await repo.update_expense_category(expense_id, cat_id)

    # Auto-save store mapping so next time this store is auto-categorized
    expense = await repo.get_expense_by_id(expense_id)
    categories = await repo.get_categories()
    cat_name = next((name for cid, name, _ in categories if cid == cat_id), "?")
    cat_icon = next((icon for cid, _, icon in categories if cid == cat_id), "")

    saved_hint = ""
    if expense and expense.description:
        pattern = expense.description.lower().strip()
        if pattern:
            await repo.add_store_mapping(pattern, cat_id, source="manual")
            saved_hint = f"\n💾 Запомнил: <b>{pattern}</b> → {cat_name}"

    await callback.message.edit_text(
        callback.message.text + f"\n{cat_icon} Категория → {cat_name}{saved_hint}",
        parse_mode="HTML",
    )
    await callback.answer("Категория обновлена!")


@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery) -> None:
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Отменено")
