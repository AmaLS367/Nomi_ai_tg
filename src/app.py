import asyncio
import logging
from aiogram import Dispatcher
from core.config import get_settings
from core.logging import setup_logging
from bot.app_bot import create_bot
from bot.handlers import commands as commands_handlers
from bot.handlers import messages as messages_handlers
from nomi.client import NomiClient
from nomi.service import NomiService

async def _main():
    s = get_settings()
    setup_logging(s.log_level)
    bot = create_bot(s.telegram_bot_token)
    dp = Dispatcher()

    nomi_client = NomiClient(api_key=s.nomi_api_key, timeout=s.request_timeout_sec)
    nomi_service = NomiService(nomi_client, s.nomi_default_nomi_uuid)

    dp.include_router(commands_handlers.setup(nomi_service))
    dp.include_router(messages_handlers.setup(nomi_service))

    logging.getLogger(__name__).info("start")
    try:
        await dp.start_polling(bot, allowed_updates=["message"])
    except asyncio.CancelledError:
        logging.getLogger(__name__).info("shutdown")
        raise

def main():
    asyncio.run(_main())

if __name__ == "__main__":
    main()
