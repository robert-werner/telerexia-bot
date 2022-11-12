from contextlib import closing
import sqlite3
import time, datetime
import random
import aiofiles
from aiogram import types
from aiogram.types import ParseMode
from aiogram.utils import executor
from datetime import datetime


from bot import dp, storage

async def weighted_already(chat_id, user_id):
    date_today = datetime.today()
    unix_date_today = time.mktime(date_today.timetuple())
    with closing(sqlite3.connect(f"./data/database/{chat_id}_weights.db")) as conn:
        with closing(conn.cursor()) as cursor:
            async with aiofiles.open("./data/sql/select_last_user_weight.sql", mode='r', encoding='utf-8') as f:
                select_user_query = await f.read()
            select_user_query = select_user_query.format(user_id=int(user_id))
            cursor.executescript(select_user_query)
            row = cursor.fetchone()
            last_weight_date = int(row[3])
            date_diff = unix_date_today - last_weight_date
            if date_diff <= 86400:
                return True
            else:
                return False

async def has_premium(user_id):
    with closing(sqlite3.connect(f"./data/database/premium_users.db")) as conn:
        with closing(conn.cursor()) as cursor:
            async with aiofiles.open("./data/sql/select_premium_user.sql", mode='r', encoding='utf-8') as f:
                select_premium_user_query = await f.read()
            select_premium_user_query = select_premium_user_query.format(user_id=int(user_id))
            cursor.executescript(select_premium_user_query)
            row = cursor.fetchone()



@dp.message_handler(lambda message: 'group' in message.chat.type, commands="help")
async def send_welcome(message: types.Message):
    """
    Send a welcome to a bot user.
    :param message:
    """
    async with aiofiles.open("./data/text/ru/help.txt", mode='r', encoding='utf-8') as f:
        contents = await f.read()
    return await message.reply(text=contents, parse_mode=ParseMode.HTML)

@dp.message_handler(lambda message: 'group' in message.chat.type, commands="weight")
async def send_weight(message: types.Message):
    """
    Send a weight to a bot user.
    :param message:
    """
    
    async with aiofiles.open("./data/sql/group_table.sql", mode='r', encoding='utf-8') as f:
        create_table_sql_statement = await f.read()
    with closing(sqlite3.connect(f"./data/database/{message.chat.id}_weights.db")) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.executescript(create_table_sql_statement)

    async with aiofiles.open("./data/text/ru/weight.txt", mode='r', encoding='utf-8') as f:
        contents = await f.read()
    return await message.reply(text=contents, parse_mode=ParseMode.HTML)

@dp.message_handler(lambda message: 'group' not in message.chat.type)
async def send_group_only(message: types.Message):
    print(message.chat.type)
    """
    Send a group only message to a bot user.
    :param message:
    """
    async with aiofiles.open("./data/text/ru/group_only.txt", mode='r', encoding='utf-8') as f:
        contents = await f.read()
    return await message.reply(text=contents, parse_mode=ParseMode.HTML)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
