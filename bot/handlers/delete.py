from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards import confirm_delete_keyboard
from db.repository import Repository

router = Router()


@router.message(Command("delete"))
async def cmd_delete(message: Message, repo: Repository) -> None:
    user = message.from_user
    if not user:
        return

    args = (message.text or "").split()
    if len(args) > 1:
        # /delete 42
        try:
            expense_id = int(args[1])
        except ValueError:
            await message.answer("Используйте: <code>/delete [id]</code>", parse_mode="HTML")
            return
    else:
        # Delete last expense
        last = await repo.get_last_expense(user.id)
        if not last:
            await message.answer("Нет расходов для удаления.")
            return
        expense_id = last.id

    kb = confirm_delete_keyboard(expense_id)
    await message.answer(f"Удалить запись #{expense_id}?", reply_markup=kb)


@router.message(Command("undo"))
async def cmd_undo(message: Message, repo: Repository) -> None:
    user = message.from_user
    if not user:
        return

    last = await repo.get_last_expense(user.id)
    if not last:
        await message.answer("Нет расходов для удаления.")
        return

    kb = confirm_delete_keyboard(last.id)
    sym = f"{last.amount:.2f} {last.currency}"
    await message.answer(
        f"Удалить последнюю запись?\n#{last.id}: {sym} — {last.description}",
        reply_markup=kb,
    )


@router.callback_query(F.data.startswith("confirmdel:"))
async def cb_confirm_delete(callback: CallbackQuery, repo: Repository) -> None:
    user = callback.from_user
    if not user:
        return

    expense_id = int(callback.data.split(":")[1])
    deleted = await repo.delete_expense(expense_id, user.id)

    if deleted:
        await callback.message.edit_text(f"🗑 Запись #{expense_id} удалена.")
    else:
        await callback.message.edit_text("Запись не найдена или уже удалена.")
    await callback.answer()


@router.callback_query(F.data.startswith("del:"))
async def cb_delete(callback: CallbackQuery, repo: Repository) -> None:
    expense_id = int(callback.data.split(":")[1])
    kb = confirm_delete_keyboard(expense_id)
    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer()
