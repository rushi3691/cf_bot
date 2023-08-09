import os
from pyrogram.types import Message 
from utils.logger import logger

class Maintainance():
    def __init__(self):
        pass
         
    def __enter__(self):
        os.environ["MODE"] = "0"
        logger.info("Maintainance mode is on")
        return self
     
    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.environ["MODE"] = "1"
        logger.info("Maintainance mode is off")

def maintainance_mode(mode: str):
    os.environ["MODE"] = mode
    if mode == "0":
        logger.info("Maintainance mode is on")
    else:
        logger.info("Maintainance mode is off")


def is_maintainance():
    return os.getenv("MODE") == "0"

async def maintainance_msg(msg: Message):
    await msg.reply("Bot is under maintainance!")
