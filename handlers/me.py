from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ChatType
import aiogram.utils.markdown as mk
from bot.db_async import User

router = Router()


@router.message(Command('me'))
async def cmd_me(message: Message, user: User) -> None:
    text = mk.hbold('💭 Информация о тебе: \n\n')
    if message.chat.type == ChatType.PRIVATE:  # Проверяем на приватность чат
        text += mk.text(mk.hbold('🆔 Твой ID:'), mk.text(user.tg_id), '\n')
    else:
        text += mk.text(mk.hbold('🆔 Твой ID:'), mk.text('В ЛС'), '\n')
    text += mk.text(
        mk.text(mk.hbold('⭐ Твой шанс:'), mk.text(str(user.chance)+'%.')),
        mk.text(mk.hbold('♻️ Твой баланс:'), mk.text(str(user.money)+' крышек.')),
        mk.text(mk.hbold('🫶 Дата регистрации:'), mk.text(user.created.strftime('%d.%m.%y'))),
        sep="\n")
    await message.answer(text, parse_mode='HTML')


