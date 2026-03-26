from __future__ import annotations

from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from db.repository import Repository
from services.chart_builder import build_comparison_chart, build_trend_chart
from services.reporter import (
    MONTH_NAMES_RU,
    PeriodRange,
    build_report,
    format_comparison,
    format_report,
    format_trend,
    get_previous_period,
    parse_period,
)

router = Router()


@router.message(Command("report"))
async def cmd_report(message: Message, repo: Repository) -> None:
    user = message.from_user
    if not user:
        return

    args = message.text.split(maxsplit=1) if message.text else []
    period_str = args[1].strip() if len(args) > 1 else None
    period = parse_period(period_str)

    currencies = await repo.get_currencies_used(user.id, period.start, period.end)
    if not currencies:
        user_currency = await repo.get_user_currency(user.id)
        currencies = [user_currency]

    parts = []
    for cur in currencies:
        report = await build_report(repo, user.id, period, cur)
        parts.append(format_report(report))

    await message.answer("\n\n".join(parts), parse_mode="HTML")


@router.message(Command("compare"))
async def cmd_compare(message: Message, repo: Repository) -> None:
    """
    Flexible comparison:
      /compare              — this month vs previous
      /compare 2026-01 2026-03  — January vs March
      /compare 6            — trend over last 6 months (chart)
      /compare 2026-01 2026-06  — trend Jan→Jun if > 2 months apart
    """
    user = message.from_user
    if not user:
        return

    args = (message.text or "").split()[1:]

    # Case 1: trend over N months  "/compare 6"
    if len(args) == 1 and args[0].isdigit():
        n_months = int(args[0])
        await _send_trend(message, repo, user.id, n_months)
        return

    # Case 2: two periods  "/compare 2026-01 2026-03"
    if len(args) == 2:
        p1 = parse_period(args[0])
        p2 = parse_period(args[1])

        # Check if it's a range of months (for trend chart)
        months_apart = _months_between(p1.start, p2.end)
        if months_apart > 2:
            await _send_trend_range(message, repo, user.id, p1.start, p2.end, months_apart)
            return

        # Two-month comparison
        await _send_comparison(message, repo, user.id, p2, p1)
        return

    # Case 3: default — this month vs previous
    period = parse_period(None)
    prev_period = get_previous_period(period)
    await _send_comparison(message, repo, user.id, period, prev_period)


async def _send_comparison(
    message: Message,
    repo: Repository,
    user_id: int,
    current_period: PeriodRange,
    previous_period: PeriodRange,
) -> None:
    currencies = await repo.get_currencies_used(user_id, current_period.start, current_period.end)
    prev_currencies = await repo.get_currencies_used(user_id, previous_period.start, previous_period.end)
    all_currencies = list(dict.fromkeys(currencies + prev_currencies))

    if not all_currencies:
        user_currency = await repo.get_user_currency(user_id)
        all_currencies = [user_currency]

    for cur in all_currencies:
        current = await build_report(repo, user_id, current_period, cur)
        previous = await build_report(repo, user_id, previous_period, cur)

        text = format_comparison(current, previous)
        await message.answer(text, parse_mode="HTML")

        # Send comparison chart
        if current.categories or previous.categories:
            buf = build_comparison_chart(
                current.categories, previous.categories,
                current_period.label, previous_period.label, cur,
            )
            photo = BufferedInputFile(buf.read(), filename="compare.png")
            await message.answer_photo(photo)


async def _send_trend(
    message: Message, repo: Repository, user_id: int, n_months: int
) -> None:
    today = date.today()
    # Go back n_months from the start of this month
    start_month = today.month - n_months
    start_year = today.year
    while start_month <= 0:
        start_month += 12
        start_year -= 1

    start = date(start_year, start_month, 1).isoformat()
    end_month = today.month + 1
    end_year = today.year
    if end_month > 12:
        end_month = 1
        end_year += 1
    end = date(end_year, end_month, 1).isoformat()

    await _send_trend_range(message, repo, user_id, start, end, n_months)


async def _send_trend_range(
    message: Message, repo: Repository, user_id: int,
    start: str, end: str, n_months: int,
) -> None:
    currencies = await repo.get_currencies_used(user_id, start, end)
    if not currencies:
        user_currency = await repo.get_user_currency(user_id)
        currencies = [user_currency]

    for cur in currencies:
        monthly = await repo.get_monthly_totals(user_id, start, end, cur)

        text = format_trend(monthly, cur, n_months)
        await message.answer(text, parse_mode="HTML")

        if monthly:
            buf = build_trend_chart(monthly, cur, n_months)
            photo = BufferedInputFile(buf.read(), filename="trend.png")
            await message.answer_photo(photo)


def _months_between(start_iso: str, end_iso: str) -> int:
    s = date.fromisoformat(start_iso)
    e = date.fromisoformat(end_iso)
    return (e.year - s.year) * 12 + (e.month - s.month)
