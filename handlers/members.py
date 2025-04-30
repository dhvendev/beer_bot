from aiogram import Router
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus
from core.db_async import give_ban
from core.config import settings

router = Router()

@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: ChatMemberUpdated):
    if event.chat.id != settings.ID_CHAT:
        return
    old = event.old_chat_member
    new = event.new_chat_member
    if new.status == ChatMemberStatus.LEFT or new.status == ChatMemberStatus.KICKED:
        await give_ban(new.user.id, '/day', 5)
