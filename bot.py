import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_API_TOKEN

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher(bot, storage=storage)