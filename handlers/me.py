from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ChatType
import aiogram.utils.markdown as mk
from bot.db_async import User

router = Router()


@router.message(Command('me'))
async def cmd_me(message: Message, user: User):
    """
    Command /me - shows user profile information
    """
    header = mk.hbold(f'🍺 Твой профиль в Beer Bot 🍺\n\n')
    
    profile_info = ""
    if message.chat.type == ChatType.PRIVATE:
        profile_info += mk.text(mk.hbold('🆔 ID:'), mk.text(user.tg_id), '\n')
    else:
        profile_info += mk.text(mk.hbold('🆔 ID:'), mk.text('Доступно в личных сообщениях'), '\n')
    
    stats = mk.text(
        mk.text(mk.hbold('🎯 Шанс успеха:'), mk.text(f'{user.chance}%')),
        mk.text(mk.hbold('💰 Баланс:'), mk.text(f'{user.money} крышек')),
        mk.text(mk.hbold('📅 В игре с:'), mk.text(user.created.strftime('%d.%m.%Y'))),
        sep="\n")
    
    tips = mk.text(
        mk.hbold('\n\n💡 Советы:'),
        mk.text('🔹 Увеличь свой шанс успеха в магазине /shop'),
        mk.text('🔹 Собирай ежедневный бонус командой /box'),
        mk.text('🔹 Испытай свою удачу командой /game'),
        sep="\n")
    
    text = header + profile_info + stats + tips
    await message.answer(text, parse_mode='HTML')