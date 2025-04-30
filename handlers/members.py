from aiogram import Router, types, Bot, F
from aiogram.filters import Command, IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import Message, InlineKeyboardButton, ChatMemberUpdated
from aiogram.enums import ChatType, ChatMemberStatus
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiogram.utils.markdown as mk
from bot.db_async import give_ban

router = Router()


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: ChatMemberUpdated):
    if event.chat.id != -1001519402420:
        return
    old = event.old_chat_member
    new = event.new_chat_member
    if new.status == ChatMemberStatus.LEFT or new.status == ChatMemberStatus.KICKED:
        await give_ban(new.user.id, '/day', 5)
    print(f'Выдан бан')
