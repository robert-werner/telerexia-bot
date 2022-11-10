import aiofiles
from aiogram import types
from aiogram.types import ParseMode
from aiogram.utils import executor

from bot import dp, storage


@dp.message_handler(commands="help")
async def send_welcome(message: types.Message):
    """
    Send a welcome to a bot user.
    :param message:
    """
    async with aiofiles.open("./data/text/ru/help.txt", mode='r', encoding='utf-8') as f:
        contents = await f.read()
    return await message.reply(text=contents, parse_mode=ParseMode.HTML)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
