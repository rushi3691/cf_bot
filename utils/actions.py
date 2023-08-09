from functools import wraps
from pyrogram import Client, enums
from pyrogram.types import Message, CallbackQuery
from typing import Union

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    async def command_func(c: Client, msg: Union[Message, CallbackQuery], *args, **kwargs):
        if isinstance(msg, Message):
            await msg.reply_chat_action(enums.ChatAction.TYPING)
        else:
            await msg.message.reply_chat_action(enums.ChatAction.TYPING)
        # context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return await func(c, msg,  *args, **kwargs)

    return command_func