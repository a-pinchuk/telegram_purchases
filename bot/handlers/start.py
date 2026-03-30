from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from bot.config import settings
from db.repository import Repository

router = Router()

HELP_TEXT = """Я помогу вести учёт расходов!

<b>Как записать расход:</b>
Просто отправь сообщение с суммой и описанием:
• <code>50 lidl</code> — сумма + магазин
• <code>50€ lidl</code> — с указанием валюты
• <code>lidl 50</code> — порядок не важен
• <code>120.50 leroy merlin</code> — дробная сумма

<b>Валюта:</b> €, ₽, zł, $, £ или коды EUR, RUB, PLN, USD, GBP
Без указания — используется ваша валюта по умолчанию.

<b>Категория:</b> бот запоминает ваш выбор — один раз выберите категорию через кнопку, и в следующий раз она определится автоматически.

<b>Команды:</b>
/report [period] — отчёт (week, month, year, 2026-03)
/chart [pie|bar] [period] — графики расходов
/compare — сравнение с прошлым месяцем
/compare 2026-01 2026-03 — сравнить два месяца
/compare 6 — тренд за последние 6 месяцев
/categories — список категорий
/addstore — привязать магазин к категории
/currency — сменить валюту по умолчанию
/delete — удалить последнюю запись
/export — экспорт в CSV
/help — эта справка"""


@router.message(CommandStart())
async def cmd_start(message: Message, repo: Repository) -> None:
    user = message.from_user
    if not user:
        return
    await repo.ensure_user(user.id, user.first_name, user.username)
    await message.answer(
        f"Привет, {user.first_name}! 👋\n\n{HELP_TEXT}",
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

    if not settings.webapp_url:
        await message.answer("Web-приложение \u043d\u0435 \u043d\u0430\u0441\u0442\u0440\u043e\u0435\u043d\u043e.")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="\U0001f4ca \u041e\u0442\u043a\u0440\u044b\u0442\u044c \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0443",
            web_app=WebAppInfo(url=settings.webapp_url),
        )]
    ])
    await message.answer("\u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u043a\u043d\u043e\u043f\u043a\u0443, \u0447\u0442\u043e\u0431\u044b \u043e\u0442\u043a\u0440\u044b\u0442\u044c \u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a\u0443 \u0440\u0430\u0441\u0445\u043e\u0434\u043e\u0432:", reply_markup=kb)
