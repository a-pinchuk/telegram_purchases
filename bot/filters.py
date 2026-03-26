from aiogram.filters import BaseFilter
from aiogram.types import Message

from services.parser import parse_expense


class ExpenseFilter(BaseFilter):
    """Matches messages that look like expense entries (contain a number)."""

    async def __call__(self, message: Message) -> bool | dict:
        if not message.text:
            return False
        # Skip commands
        if message.text.startswith("/"):
            return False
        result = parse_expense(message.text)
        if result is None:
            return False
        return {"parsed": result}
