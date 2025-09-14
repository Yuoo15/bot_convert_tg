from xml.sax import handler
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Dict, Any
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class CheckLink(BaseMiddleware):

    async def __call__(self, 
    handler:Callable[[Message, Dict[str, Any]], Awaitable[Any]],
    event:Message,
    data: Dict[str, Any]
    )->Any:
        chat_member = await event.bot.get_chat_member("@testBots_ram", event.from_user.id)
        if chat_member.status == "left":
            await event.answer('Что-бы продолжить, подпишитесь на канал', reply_markup=main)
        else:
            return await handler(event, data)      

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подписаться', url='https://t.me/testBots_ram')]
])
