import html

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton
from aiogram.enums import ChatType
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.other.replies import LINK_BOT, BEER_UNIT
from bot.db_async import update_count_drink
import aiogram.utils.markdown as mk
from sqlalchemy.ext.asyncio import AsyncSession
from bot.db_async import User, Chat, update_drink

router = Router()


@router.message(Command('drink'), F.chat.type == ChatType.PRIVATE)
async def cmd_drink(message: Message):
    text = mk.text(mk.hbold('Команда /drink'), "доступна везде кроме лс бота🍺")
    await message.answer(text, parse_mode='HTML')
    return


@router.message(Command('drink'), F.chat.type != ChatType.PRIVATE)
async def cmd_drink(message: Message, session: AsyncSession,
                    user: User, chat: Chat):
    result, list_gamer, update_count = await update_drink(session, user, chat)
    position = [i[0].user_id for i in list_gamer].index(user.id) + 1 #Вычисляем позицию игрока
    text_link = mk.hlink(user.name, f"https://t.me/{user.link}") if user.link != 'unknown' else mk.html_decoration.quote(user.name)
    if update_count:
        text_doing = mk.hbold('ВЫБУХАЛ')
        if update_count < 0:
            text_doing = mk.hbold('ВЫБЛЕВАЛ')
        text = mk.text(
            f"👻{text_link}, сегодня ты {text_doing} | {mk.hbold(update_count)} {BEER_UNIT}\n",
            f"Теперь твой ПИВзапас {mk.hbold(round(result.count,1))} {BEER_UNIT}",
            f"💀Ты занимаешь {mk.hbold(position)} место",
            "Следующая попытка завтра!",mk.hlink("Крути какашки💩", "https://t.me/boinker_bot/boinkapp?startapp=boink965898224"),mk.hlink("Кидай монетку🪙", "https://t.me/CoinFlipGame_bot/DOXCoinFlip?startapp=965898224"),
            sep='\n')
        return await message.answer(text, parse_mode='HTML', disable_web_page_preview=True)
    text = mk.text(
        f"👻{text_link}, ты уже пил сегодня\n",
        f"Твой запас: {mk.hbold(round(result.count,1))} {BEER_UNIT}",
        f"💀В местном топчике ты на {mk.hbold(position)} месте",
        "Следующая попытка завтра!",mk.hlink("Крути какашки💩", "https://t.me/boinker_bot/boinkapp?startapp=boink965898224"),mk.hlink("Кидай монетку🪙", "https://t.me/CoinFlipGame_bot/DOXCoinFlip?startapp=965898224"),
        sep='\n')
    return await message.answer(text, parse_mode='HTML', disable_web_page_preview=True)


