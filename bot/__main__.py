import asyncio
import logging

import uvicorn
from aiogram import Bot, Dispatcher

from bot.config import settings
from db.repository import Repository
from webapp.main import create_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    repo = Repository(settings.db_path)
    await repo.init()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp["repo"] = repo
    dp["settings"] = settings

    # Access control
    from bot.middlewares import AccessMiddleware
    dp.update.middleware(AccessMiddleware(settings))

    # Import and include routers
    from bot.handlers.start import router as start_router
    from bot.handlers.expense import router as expense_router
    from bot.handlers.report import router as report_router
    from bot.handlers.chart import router as chart_router
    from bot.handlers.categories import router as categories_router
    from bot.handlers.delete import router as delete_router
    from bot.handlers.export import router as export_router

    dp.include_router(start_router)
    dp.include_router(report_router)
    dp.include_router(chart_router)
    dp.include_router(categories_router)
    dp.include_router(delete_router)
    dp.include_router(export_router)
    dp.include_router(expense_router)  # last — catches plain text

    # FastAPI web app
    app = create_app()
    app.state.repo = repo
    app.state.bot_token = settings.bot_token

    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)

    logger.info("Starting bot + web server on :8080 ...")
    try:
        await asyncio.gather(
            dp.start_polling(bot),
            server.serve(),
        )
    finally:
        await repo.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
