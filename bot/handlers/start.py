import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from bot.config import settings
from db.repository import Repository

logger = logging.getLogger(__name__)

router = Router()

HELP_TEXT = """\u042f \u043f\u043e\u043c\u043e\u0433\u0443 \u0432\u0435\u0441\u0442\u0438 \u0443\u0447\u0451\u0442 \u0440\u0430\u0441\u0445\u043e\u0434\u043e\u0432!

<b>\u041a\u0430\u043a \u0437\u0430\u043f\u0438\u0441\u0430\u0442\u044c \u0440\u0430\u0441\u0445\u043e\u0434:</b>
\u041f\u0440\u043e\u0441\u0442\u043e \u043e\u0442\u043f\u0440\u0430\u0432\u044c \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u0441 \u0441\u0443\u043c\u043c\u043e\u0439 \u0438 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435\u043c:
\u2022 <code>50 lidl</code> \u2014 \u0441\u0443\u043c\u043c\u0430 + \u043c\u0430\u0433\u0430\u0437\u0438\u043d
\u2022 <code>50\u20ac lidl</code> \u2014 \u0441 \u0443\u043a\u0430\u0437\u0430\u043d\u0438\u0435\u043c \u0432\u0430\u043b\u044e\u0442\u044b
\u2022 <code>lidl 50</code> \u2014 \u043f\u043e\u0440\u044f\u0434\u043e\u043a \u043d\u0435 \u0432\u0430\u0436\u0435\u043d
\u2022 <code>120.50 leroy merlin</code> \u2014 \u0434\u0440\u043e\u0431\u043d\u0430\u044f \u0441\u0443\u043c\u043c\u0430

<b>\u0412\u0430\u043b\u044e\u0442\u0430:</b> \u20ac, \u20bd, z\u0142, $, \u00a3 \u0438\u043b\u0438 \u043a\u043e\u0434\u044b EUR, RUB, PLN, USD, GBP
\u0411\u0435\u0437 \u0443\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u2014 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u0442\u0441\u044f \u0432\u0430\u0448\u0430 \u0432\u0430\u043b\u044e\u0442\u0430 \u043f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e.

<b>\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f:</b> \u0431\u043e\u0442 \u0437\u0430\u043f\u043e\u043c\u0438\u043d\u0430\u0435\u0442 \u0432\u0430\u0448 \u0432\u044b\u0431\u043e\u0440 \u2014 \u043e\u0434\u0438\u043d \u0440\u0430\u0437 \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044e \u0447\u0435\u0440\u0435\u0437 \u043a\u043d\u043e\u043f\u043a\u0443, \u0438 \u0432 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439 \u0440\u0430\u0437 \u043e\u043d\u0430 \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0438\u0442\u0441\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438.

<b>\u041a\u043e\u043c\u0430\u043d\u0434\u044b:</b>
/report [period] \u2014 \u043e\u0442\u0447\u0451\u0442 (week, month, year, 2026-03)
/chart [pie|bar] [period] \u2014 \u0433\u0440\u0430\u0444\u0438\u043a\u0438 \u0440\u0430\u0441\u0445\u043e\u0434\u043e\u0432
/compare \u2014 \u0441\u0440\u0430\u0432\u043d\u0435\u043d\u0438\u0435 \u0441 \u043f\u0440\u043e\u0448\u043b\u044b\u043c \u043c\u0435\u0441\u044f\u0446\u0435\u043c
/compare 2026-01 2026-03 \u2014 \u0441\u0440\u0430\u0432\u043d\u0438\u0442\u044c \u0434\u0432\u0430 \u043c\u0435\u0441\u044f\u0446\u0430
/compare 6 \u2014 \u0442\u0440\u0435\u043d\u0434 \u0437\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0435 6 \u043c\u0435\u0441\u044f\u0446\u0435\u0432
/categories \u2014 \u0441\u043f\u0438\u0441\u043e\u043a \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0439
/addstore \u2014 \u043f\u0440\u0438\u0432\u044f\u0437\u0430\u0442\u044c \u043c\u0430\u0433\u0430\u0437\u0438\u043d \u043a \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438
/currency \u2014 \u0441\u043c\u0435\u043d\u0438\u0442\u044c \u0432\u0430\u043b\u044e\u0442\u0443 \u043f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e
/delete \u2014 \u0443\u0434\u0430\u043b\u0438\u0442\u044c \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u044e\u044e \u0437\u0430\u043f\u0438\u0441\u044c
/export \u2014 \u044d\u043a\u0441\u043f\u043e\u0440\u0442 \u0432 CSV
/app \u2014 \u043e\u0442\u043a\u0440\u044b\u0442\u044c \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0443
/help \u2014 \u044d\u0442\u0430 \u0441\u043f\u0440\u0430\u0432\u043a\u0430"""


@router.message(CommandStart())
async def cmd_start(message: Message, repo: Repository) -> None:
    user = message.from_user
    if not user:
        return
    await repo.ensure_user(user.id, user.first_name, user.username)
    await message.answer(
        f"\u041f\u0440\u0438\u0432\u0435\u0442, {user.first_name}! \U0001f44b\n\n{HELP_TEXT}",
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML")


@router.message(Command("app"))
async def cmd_app(message: Message, repo: Repository) -> None:
    user = message.from_user
    if not user:
        return

    logger.info(f"/app command from user={user.id} chat_type={message.chat.type} chat_id={message.chat.id}")

    if not settings.webapp_url:
        await message.answer("Web-\u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u043d\u0435 \u043d\u0430\u0441\u0442\u0440\u043e\u0435\u043d\u043e.")
        return

    is_private = message.chat.type == "private"

    if is_private:
        try:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="\U0001f4ca \u041e\u0442\u043a\u0440\u044b\u0442\u044c \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0443",
                    web_app=WebAppInfo(url=settings.webapp_url),
                )]
            ])
            await message.answer(
                "\u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u043a\u043d\u043e\u043f\u043a\u0443:",
                reply_markup=kb,
            )
        except Exception as e:
            logger.error(f"/app web_app button failed: {e}")
            await message.answer(f"\U0001f4ca \u0410\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430: {settings.webapp_url}")
    else:
        # Group chat: web_app buttons DON'T work (Telegram API limitation).
        # Send a direct t.me link that opens Mini App inside Telegram.
        try:
            link = f"https://t.me/pinchuk_life_bot/tracker"
            await message.answer(
                f"\U0001f4ca <b>\u0410\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430 \u0440\u0430\u0441\u0445\u043e\u0434\u043e\u0432</b>\n\n"
                f"\u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u0441\u0441\u044b\u043b\u043a\u0443 \u0447\u0442\u043e\u0431\u044b \u043e\u0442\u043a\u0440\u044b\u0442\u044c:\n"
                f"{link}",
                parse_mode="HTML",
            )
            logger.info(f"/app sent link to group chat {message.chat.id}")
        except Exception as e:
            logger.error(f"/app group handler failed: {e}")
            await message.answer(f"\U0001f4ca \u0410\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0430: {settings.webapp_url}")
