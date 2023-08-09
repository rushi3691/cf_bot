from dotenv import load_dotenv
load_dotenv()
from client.client import bot
from pyrogram import idle
from handler.admin import *
from handler.handler import *
from database.db import db
import asyncio

# fastapi dependencies
from fastapi import FastAPI
import uvicorn
from uvicorn import Server
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request



app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



async def main():
    config = uvicorn.Config("bot:app", host="0.0.0.0", port=8000, workers=1)
    await bot.start()
    server = Server(config = config)
    api = asyncio.create_task(server.serve())
    _bot = asyncio.create_task(idle())

    await asyncio.wait([api, _bot])
    await db.disconnect()
    await bot.stop()

if __name__ == "__main__":
    bot.run(main())


# commands for bot
# start - create database
# auth - login 
# token - send token 
# fetch - create database 
# get - get questions
# pg - current progress (/pg level1 level2 ..)
# set_level - change level, default 800 (/set_level level)
# hello - greeting
# update - manually update database
# ls - show files in bot dir
# get_db - get database
# user_info - user info
# reset_p - reset progress (/reset_p yes)
# del_db - delete database