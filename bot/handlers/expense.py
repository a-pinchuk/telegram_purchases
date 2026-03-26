from aiogram import Router
from aiogram.types import Message

from bot.filters import ExpenseFilter
from bot.keyboards import expense_actions_keyboard
from db.repository import Repository
from services.categorizer import categorize
from services.parser import ParsedExpense

router = Router()


@router.message(ExpenseFilter())
async def handle_expense(message: Message, parsed: ParsedExpense, repo: Repository) -> None:
    user = message.from_user
    if not user:
        return

    await repo.ensure_user(user.id, user.first_name, user.username)

    # Determine currency
    currency = parsed.currency
    if not currency:
        currency = await repo.get_user_currency(user.id)

    # Categorize
    cat_result = await categorize(parsed.description, repo)

    category_id = cat_result.category_id if cat_result else None
    store = cat_result.matched_pattern if cat_result else None

    # Save
    expense_id = await repo.add_expense(
        user_id=user.id,
        amount=parsed.amount,
        currency=currency,
        description=parsed.description,
        category_id=category_id,
        store=store,
    )

    # Format response
    currency_symbol = _currency_symbol(currency)
    amount_str = f"{parsed.amount:,.2f}{currency_symbol}"
    desc_display = parsed.description.title() if parsed.description else "Без описания"

    if cat_result:
        text = f"✅ {amount_str} — {desc_display} ({cat_result.category_name} {cat_result.category_icon})"
    else:
        text = f"✅ {amount_str} — {desc_display} (без категории 📦)"

    text += f"\n🆔 #{expense_id}"

    kb = expense_actions_keyboard(expense_id)
    await message.answer(text, reply_markup=kb)


CURRENCY_SYMBOLS = {
    "EUR": " €",
    "RUB": " ₽",
    "PLN": " zł",
    "USD": " $",
    "GBP": " £",
    "CZK": " Kč",
}


def _currency_symbol(code: str) -> str:
    return CURRENCY_SYMBOLS.get(code, f" {code}")
