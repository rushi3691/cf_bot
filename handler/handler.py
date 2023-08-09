from socket import setdefaulttimeout
from client.client import bot
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils.actions import send_typing_action
from utils.logger import logger
from utils.maintainance import is_maintainance, maintainance_msg
import os
from database.db import *
from tabulate import tabulate
import zlib


user_config = {} # user_id, user_level, 

def edit_config(user_id: int, user_level: int = None, easy_count: int = None, medium_count: int = None, hard_count: int = None):
    set_default_config(user_id)
    if user_level:
        user_config[user_id]['user_level'] = user_level
    if easy_count:
        user_config[user_id]['easy_count'] = easy_count
    if medium_count:
        user_config[user_id]['medium_count'] = medium_count
    if hard_count:
        user_config[user_id]['hard_count'] = hard_count


def set_default_config(user_id: int):
    if user_id in user_config:
        return
    user_config[user_id] = {
        'user_level': int(os.getenv('USER_LEVEL')),
        'easy_count': int(os.getenv('EASY_COUNT')),
        'medium_count': int(os.getenv('MEDIUM_COUNT')),
        'hard_count': int(os.getenv('HARD_COUNT'))
    }

@bot.on_message(filters.regex("^/start$"))
@send_typing_action
async def start(c, msg: Message):
    user_id = msg.chat.id
    set_default_config(user_id)
    return await msg.reply_text("Welcome to bot!")

@bot.on_message(filters.regex("^/set_level \d+$"))
@send_typing_action
async def set_level(c, msg: Message):
    if is_maintainance():
        return await maintainance_msg(msg) 
    user_id = msg.chat.id
    try:
        str_lvl = msg.text.split()[1]
        new_level = int(str_lvl)
        if new_level < 800:
            return await msg.reply(f"level should be >= 800") 
        edit_config(user_id, new_level)
        await msg.reply(f"set user level to {new_level}")
    except Exception as e:
        logger.error(e)
        await msg.reply_text("Some error has occured!\ncmd: /set_level")

@bot.on_message(filters.regex("^/user_info$"))
@send_typing_action
async def get_user_info(c, msg: Message):
    if is_maintainance():
        return await maintainance_msg(msg)
    user_id = msg.chat.id
    set_default_config(user_id)
    try:
        txt = f"""USER_LEVEL = {user_config[user_id]['user_level']}\nEASY_COUNT = {user_config[user_id]['easy_count']}\nMEDIUM_COUNT = {user_config[user_id]['medium_count']}\nHARD_COUNT = {user_config[user_id]['hard_count']}"""
        await msg.reply(txt)
    except Exception as e:
        logger.error(e)
        await msg.reply_text("Some error has occured!\ncmd: /user_info")

@bot.on_message(filters.regex("^/get$"))
@send_typing_action
async def send_qs(c, msg: Message): 
    if is_maintainance():
        return await maintainance_msg(msg)
    # try:
    user_id = msg.chat.id
    set_default_config(user_id)
    level = user_config[user_id]['user_level']
    data = await get_randqs(level, user_id, user_config)
    text = ""
    payload = ""
    for i in data:
        text += f"[{i['name']}](https://codeforces.com/problemset/problem/{i['contestid']}/{i['qindex']})\n"
        payload += f"{i['qid']} "
    payload = payload.strip()
    # logger.info(f"payload: {payload}")
    payload = zlib.compress(payload.encode())
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("mark all",callback_data=payload)]])
    await msg.reply(text, disable_web_page_preview=True, reply_markup=reply_markup)
    # except Exception as e:
    #     logger.error(e)
    #     await msg.reply("wrong input\n/get [level:int]")

@bot.on_callback_query()
@send_typing_action
async def markdone(c, cq: CallbackQuery):
    if is_maintainance():
        return await maintainance_msg(cq.message)

    msg = await cq.message.reply("updating progress...wait")
    try:
        x = (zlib.decompress(cq.data).decode()).split()
        # x = (cq.data).split()
        user_id = cq.message.chat.id
        data = []
        for i in x:
            data.append({'question_id':i})
        # print(x)
        # print(data)
        await mark_done_many(data, user_id)
        await msg.edit("congratulations!\nQuestions marked as done")
        await cq.message.delete()
    except Exception as e:
        logger.error(e)
        await msg.edit("Some error has occured!\ncmd: /auth")

@bot.on_message(filters.regex("^/reset_p yes$"))
@send_typing_action
async def reset_progress(c, msg: Message):
    if is_maintainance():
        return await maintainance_msg(msg)

    m = await msg.reply("resetting progress...wait")
    user_id = msg.chat.id
    try:
        await reset_p(user_id)
        await m.edit("progress reseted.")
    except Exception as e:
        logger.error(e)
        await m.edit("Some error has occured!\ncmd: /reset_p")

@bot.on_message(filters.regex("^/pg"))
@send_typing_action
async def get_progress(c, msg:Message):
    if is_maintainance():
        return await maintainance_msg(msg)

    args = msg.text.split()[1:]
    user_id = msg.chat.id
    try:
        ls = []
        ls.append(await show_p(user_id))
        if args:
            for i in args:
                ls.append(await show_p(user_id, i))

        ans = tabulate(ls, headers=["id", "Question"])
        await msg.reply(f"```{ans}```")
    except Exception as e:
        logger.error(e)
        await msg.reply_text("Some error has occured!\ncmd: /pg")

