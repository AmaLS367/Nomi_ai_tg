from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

def create_bot(token: str) -> Bot:
    return Bot(token=token, default=DefaultBotProperties(parse_mode=None))
