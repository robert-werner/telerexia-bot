import datetime
import random
import sqlite3
import time
from contextlib import closing
from datetime import datetime
from sqlalchemy import text
from enum import Enum

import aiofiles
from aiogram import types
from aiogram.types import ParseMode
from aiogram.utils import executor
from sqlalchemy.ext.asyncio import create_async_engine

from config import DATABASE_URI


class WeightAction(Enum):
    GONE_UP = """твой вес увеличился на {weight_diff_kg} килограмм(а).\n\nТвой текущий вес: {current_weight_kg} килограмм(а)
    """
    GONE_DOWN = """поздравляю! Твой вес уменьшился на {weight_diff_kg} килограмм(а).\n\nТвой текущий вес: {current_weight_kg} килограмм(а)
    """
    EQUAL = """твой вес не изменился (или ты взвешиваешься в первый раз).\n\nТвой текущий вес: {current_weight_kg} килограмм(а)"""


from bot import dp


async def weighted_already(chat_id, user_id):
    date_today = datetime.today()
    unix_date_today = time.mktime(date_today.timetuple())
    engine = create_async_engine(DATABASE_URI, echo=True)
    async with engine.connect() as conn:
        async with aiofiles.open("./data/sql/select_last_user_weight.sql", mode='r', encoding='utf-8') as f:
            select_user_query = await f.read()
        select_user_query = select_user_query.format(user_id=int(user_id), group_id=int(chat_id))
        result = await conn.execute(text(select_user_query))
        row = result.fetchone()
        if not row:
            return False
        last_weight_date = int(row[4])
        date_diff = unix_date_today - last_weight_date
        if date_diff <= 10:
            return True
        else:
            return False


async def last_weight(chat_id, user_id):
    engine = create_async_engine(DATABASE_URI)
    async with engine.connect() as conn:
        async with aiofiles.open("./data/sql/select_last_user_weight.sql", mode='r', encoding='utf-8') as f:
            select_user_query = await f.read()
        select_user_query = select_user_query.format(user_id=int(user_id), group_id=int(chat_id))
        result = await conn.execute(text(select_user_query))
        row = result.fetchone()
        if not row:
            return 0
        last_weight_grams = int(row[3])
        return last_weight_grams


async def write_weight(chat_id, user_id, weight):
    engine = create_async_engine(DATABASE_URI)
    async with engine.connect() as conn:
        date_today = datetime.today()
        unix_date_today = time.mktime(date_today.timetuple())
        async with aiofiles.open("./data/sql/insert_weight.sql", mode='r', encoding='utf-8') as f:
            insert_weight_query = await f.read()
        user_insert_weight_query = insert_weight_query.format(user_id=user_id, group_id=chat_id, weight=weight,
                                                              unix_time=unix_date_today)
        await conn.execute(text(user_insert_weight_query))
        await conn.commit()


@dp.message_handler(lambda message: 'group' in message.chat.type, commands="help")
async def send_welcome(message: types.Message):
    """
    Send a welcome to a bot user.
    :param message:
    """
    async with aiofiles.open("./data/text/ru/help.txt", mode='r', encoding='utf-8') as f:
        contents = await f.read()
    return await message.reply(text=contents, parse_mode=ParseMode.HTML)


@dp.message_handler(lambda message: 'group' in message.chat.type, commands="top10")
async def send_local_top_weight(message: types.Message):
    """
    Send local top-10 weight to a bot user.
    :param message:
    """


@dp.message_handler(lambda message: 'group' in message.chat.type, commands="global")
async def send_global_top_weight(message: types.Message):
    """
    Send global top-10 weight to a bot user.
    :param message:
    """


@dp.message_handler(lambda message: 'group' in message.chat.type, commands="weight")
async def send_weight(message: types.Message):
    """
    Send a weight to a bot user.
    :param message:
    """

    user_weighted_already = await weighted_already(message.chat.id, message.from_user.id)
    if not user_weighted_already:
        async with aiofiles.open("./data/text/ru/weight.txt", mode='r', encoding='utf-8') as f:
            contents = await f.read()
        random_weight = random.randint(0, 100000)
        while random_weight < 0:
            random_weight = random.randint(0, 100000)
        user_last_weight = await last_weight(message.chat.id, message.from_user.id)
        weight_diff = abs(random_weight - user_last_weight)
        weight_diff_kg = weight_diff / 1000
        current_weight = user_last_weight + weight_diff
        current_weight_kg = current_weight / 1000
        if weight_diff > 0:
            diff_description = WeightAction.GONE_UP.value
        elif weight_diff < 0:
            diff_description = WeightAction.GONE_DOWN.value
        elif weight_diff == 0:
            diff_description = WeightAction.EQUAL.value
        await write_weight(message.chat.id, message.from_user.id, current_weight)
        diff_description = diff_description.format(
            weight_diff=weight_diff,
            weight_diff_kg=weight_diff_kg,
            current_weight=current_weight,
            current_weight_kg=current_weight_kg
        )
        message_contents = contents.format(
            user_name=message.from_user.full_name,
            user_id=message.from_user.id,
            weight_action=diff_description,
            place=0,
            premium_message='yes'
        )
    else:
        async with aiofiles.open("./data/text/ru/weighted_already.txt", mode='r', encoding='utf-8') as f:
            contents = await f.read()
        message_contents = contents.format(
            user_name=message.from_user.full_name,
            user_id=message.from_user.id,
        )
    return await message.reply(text=message_contents, parse_mode=ParseMode.HTML)


@dp.message_handler(lambda message: 'group' not in message.chat.type)
async def send_group_only(message: types.Message):
    """
    Send a group only message to a bot user.
    :param message:
    """
    async with aiofiles.open("./data/text/ru/group_only.txt", mode='r', encoding='utf-8') as f:
        contents = await f.read()
    return await message.reply(text=contents, parse_mode=ParseMode.HTML)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
