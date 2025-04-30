from typing import Callable, Awaitable, Dict, Any
from aiogram.types import Message, CallbackQuery
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
from core.db_async import async_session, get_or_add_user, get_or_add_chat
from aiogram.enums import ChatType


class DbSessionAndCheckRegister(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        async with async_session() as session:
            data["session"] = session
            tg_id = event.from_user.id
            name = event.from_user.first_name or "unknown"
            link = event.from_user.username or "unknown"
            user = await get_or_add_user(session, tg_id, name, link)
            data["user"] = user
            if event.chat.type != ChatType.PRIVATE:
                chat_id = event.chat.id
                chat_title = event.chat.title or 'unknown'
                chat = await get_or_add_chat(session, chat_id, chat_title)
                data["chat"] = chat
            return await handler(event, data)