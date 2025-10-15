from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from nomi.service import NomiService

router = Router()

def setup(service: NomiService) -> Router:
    @router.message(CommandStart())
    async def start(m: Message):
        await m.answer(
            "👋 Hi! I’m your Telegram companion powered by Nomi.ai.\n"
            "• Send a message to chat\n"
            "• /status — show active Nomi\n"
            "• /help — quick tips"
        )

    @router.message(Command("status"))
    async def status(m: Message):
        nid, name = await service.ensure_default()
        label = f"{name} ({nid})" if name else nid
        await m.answer(f"Active Nomi: {label}")

    @router.message(Command("help"))
    async def help_cmd(m: Message):
        await m.answer(
            "Commands:\n"
            "/start - connect and show info\n"
            "/status - show active Nomi\n\n"
            "Images and media:\n"
            "Nomi API does not accept direct file uploads. Send a file URL in the message or in the caption, for example https://example.com/image.jpg. I will forward it."
        )

    return router
