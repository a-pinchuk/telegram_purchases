from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from db.repository import Repository
from services.chart_builder import build_bar_chart, build_pie_chart
from services.reporter import parse_period

router = Router()


@router.message(Command("chart"))
async def cmd_chart(message: Message, repo: Repository) -> None:
    user = message.from_user
    if not user:
        return

    args = (message.text or "").split()[1:]  # skip "/chart"
    chart_type = "pie"
    period_str = None

    for arg in args:
        if arg in ("pie", "bar"):
            chart_type = arg
        else:
            period_str = arg

    period = parse_period(period_str)
    currencies = await repo.get_currencies_used(user.id, period.start, period.end)

    if not currencies:
        await message.answer("Нет расходов за этот период.")
        return

    for cur in currencies:
        if chart_type == "pie":
            categories = await repo.get_category_totals(user.id, period.start, period.end, cur)
            buf = build_pie_chart(categories, period.label, cur)
        else:
            daily = await repo.get_daily_totals(user.id, period.start, period.end, cur)
            buf = build_bar_chart(daily, period.label, cur)

        photo = BufferedInputFile(buf.read(), filename=f"chart_{cur}.png")
        await message.answer_photo(photo)
