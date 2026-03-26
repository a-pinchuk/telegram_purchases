from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from db.repository import Repository
from services.exporter import export_csv
from services.reporter import parse_period

router = Router()


@router.message(Command("export"))
async def cmd_export(message: Message, repo: Repository) -> None:
    user = message.from_user
    if not user:
        return

    args = (message.text or "").split()[1:]
    period_str = args[0] if args else None
    period = parse_period(period_str)

    expenses = await repo.get_expenses(user.id, period.start, period.end)
    if not expenses:
        await message.answer("Нет расходов за этот период.")
        return

    buf = export_csv(expenses)
    doc = BufferedInputFile(buf.read(), filename=f"expenses_{period.label}.csv")
    await message.answer_document(doc, caption=f"📎 Экспорт за {period.label} ({len(expenses)} записей)")
