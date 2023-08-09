from pyrogram import Client
import os

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
bot = Client(
    "bot", api_id, api_hash, bot_token=bot_token,
    # in_memory=True,
)
