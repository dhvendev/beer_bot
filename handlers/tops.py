from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton
from aiogram.enums import ChatType
import aiogram.utils.markdown as mk
from core.db_async import get_top_local, get_top_global, get_top, get_fulltop

from core.db_async import User, Chat
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.other.replies import LINK_BOT
router = Router()


def filter_name(user):
    text_link = mk.hlink(user.name, f"https://t.me/{user.link}") if user.link != 'unknown' else mk.html_decoration.quote(user.name)
    return text_link


@router.message(Command('top'), F.chat.type != ChatType.PRIVATE)
async def cmd_top(message: Message, session: AsyncSession, user: User, chat: Chat):
    list_gamer = await get_top(session, user, chat)
    text = mk.hbold("🍺 Местный топчик:\n\n")
    text = text + '\n'.join([f"{pos}. {filter_name(user)} {mk.hbold(round(count.count, 1))} л.🍺" for pos, (user, count) in enumerate(list_gamer, 1)])
    await message.answer(text, parse_mode='HTML', disable_web_page_preview=True)


@router.message(Command('top'), F.chat.type == ChatType.PRIVATE)
async def cmd_top(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Перейти в ЛС✌",
        url=LINK_BOT))
    text = mk.text(mk.hbold('Команда /top'), "доступна везде кроме лс бота🍺")
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
    return


@router.message(Command('fulltop'), F.chat.type != ChatType.PRIVATE)
async def cmd_fulltop(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Перейти в ЛС✌",
        url=LINK_BOT))
    text = mk.text(mk.hbold('Команда /fulltop'), "доступна только в лс бота🍺")
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
    return


@router.message(Command('fulltop'), F.chat.type == ChatType.PRIVATE)
async def cmd_fulltop(message: Message, session: AsyncSession):
    list_gamer = await get_fulltop(session)
    text = mk.hbold("🍺 Глобальный топчик:\n\n")
    text = text + '\n'.join([f"{pos}. {filter_name(user)} {mk.hbold(round(count.count, 1))} л.🍺" for pos, (user, count) in enumerate(list_gamer, 1)])
    await message.answer(text, parse_mode='HTML', disable_web_page_preview=True)
    return
