from pyrogram.types import Message
from pyrogram import filters
from client.client import bot
from database.db import *
from utils.user_conf import Lock
from utils.maintainance import *
from utils.actions import send_typing_action

admin_users=[123] # replace with your admin user ids
MODES = {"0", "1"}


@bot.on_message(filters.user(admin_users) & filters.regex("^/commands$"))
@send_typing_action
async def get_admin_commands(c, msg: Message):
    m = """create_db\nupdate_db\nset_mode \d\nmigrate"""
    await msg.reply(m)

@bot.on_message(filters.user(admin_users) & filters.regex("^/update_db$"))
@send_typing_action
async def update_db(c,msg: Message):
    # async with Lock:
    m = await msg.reply("updating the database...wait")

    with Maintainance():
        await create_Questions_table()
        await insert_questions()
        await asyncio.sleep(2)

    await m.edit("database updated successfully!")

@bot.on_message(filters.user(admin_users) & filters.regex("^/set_mode \d$"))
@send_typing_action
async def set_mode(c, msg: Message):
    # async with Lock:
    try:
        mode = msg.text.split()[1].strip()
        logger.info(f"\"{mode}\"")
        
        if mode not in MODES:
            return await msg.reply(f"mode can only be either 0 or 1")
        maintainance_mode(mode)
        await msg.reply(f"ENV: MODE set to {mode}")
    except:
        await msg.reply("Pass mode!")

@bot.on_message(filters.user(admin_users) & filters.regex("^/migrate$"))
@send_typing_action
async def migrate(c, msg: Message):
    # async with Lock:
    with Maintainance():
        await create_table()
        await insert_questions()

@bot.on_message(filters.user(admin_users) & filters.regex("^/disconnect$"))
@send_typing_action
async def disconnect_db(c, msg: Message):
    # async with Lock:
    with Maintainance():
        await db.disconnect()