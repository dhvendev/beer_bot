from random import randint
from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, InlineKeyboardButton
from aiogram.enums import ChatType, ChatMemberStatus
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils import markdown as mk
from core.db_async import check_ban, box
from core.config import settings
from datetime import datetime


class CallbackBox(CallbackData, prefix='box_day'):
    text: str

PRIZES = {
    40: 5,    # 0-39: 5 крышек (40% шанс)
    65: 10,   # 40-64: 10 крышек (25% шанс)
    85: 20,   # 65-84: 20 крышек (20% шанс)
    95: 30,   # 85-94: 30 крышек (10% шанс)
    100: 50   # 95-99: 50 крышек (5% шанс)
}


def get_random_prize() -> int:
    """
    Возвращает случайную награду на основе заданной вероятности.

    Returns:
        int: Количество крышек в награду
    """
    random_number = randint(0, 99)
    for threshold, prize in PRIZES.items():
        if random_number < threshold:
            return prize
    return 5

router = Router()


@router.message(Command('day'), F.chat.type != ChatType.PRIVATE)
async def cmd_day(message: Message, bot: Bot) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Перейти в ЛС✌",
        url=settings.LINK_BOT
    ))
    text = mk.text(mk.hbold('Ежедневные коробки'), "доступны только в лс бота🍺")
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
    return


@router.message(Command('day'))
async def cmd_day(message: Message, bot: Bot) -> None:
    tg_id = message.from_user.id

    # Проверяем подписку на NEWS
    check_subscribe = await bot.get_chat_member(settings.ID_NEWS, tg_id)
    if check_subscribe.status == ChatMemberStatus.LEFT or check_subscribe.status == ChatMemberStatus.KICKED:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Подписаться на новости 📰",
            url=settings.LINK_NEWS
        ))
        text = mk.text(mk.hbold('Для доступа необходима подписка на наш новостной канал 🔥'))
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
        return

    # Проверяем подписку на CHAT
    check_subscribe = await bot.get_chat_member(settings.ID_CHAT, tg_id)
    if check_subscribe.status == ChatMemberStatus.LEFT or check_subscribe.status == ChatMemberStatus.KICKED:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Присоединиться к чату 💬",
            url=settings.LINK_CHAT
        ))
        text = mk.text(mk.hbold('Присоединитесь к нашему сообществу, чтобы продолжить 🚀'))
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
        return
    
    name = message.from_user.first_name or "unknown"
    link = message.from_user.username or "unknown"

    # Проверяем не заблокирован ли пользователь
    ban = await check_ban(tg_id, name, link, '/day')
    if ban:
        expiration_time = ban.expiration
        text = mk.text(
            mk.hbold('⚠️ Доступ к призам временно ограничен'),
            mk.text('Ограничение действует до:', mk.hbold(expiration_time.strftime("%d.%m.%Y %H:%M"))),
            mk.text(f'Считаете, что произошла ошибка? Напишите {settings.ADMIN_USERNAME} для выяснения ситуации'),
            sep='\n'
        )
        await message.answer(text, parse_mode='HTML')
        return

    builder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text="🎁", callback_data=CallbackBox(text='box').pack()) for _ in range(9)]
    builder.row(*buttons, width=3)
    text = mk.hbold('Выбирай коробку и забирай свой бонус 🍺')
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
    return


@router.callback_query(CallbackBox.filter(F.text == 'box'))
async def process_button(callback: types.CallbackQuery):
    tg_id = callback.from_user.id
    name = callback.from_user.first_name or "unknown"
    link = callback.from_user.username or "unknown"
    try:
        result = get_random_prize()  

        data_box, status = await box(tg_id, name, link, result)
        if not status:
            text = mk.text(
                mk.hbold(f"🎁 Ваш ежедневный приз уже получен!"),
                mk.text(f"Вы открыли коробку {data_box.created.strftime('%d.%m')} в {data_box.created.strftime('%H:%M')}"),
                mk.text('Возвращайтесь завтра за новыми подарками 🕙'),
                mk.text(f'<span class="tg-spoiler">А пока можете развлечься в нашей мини-игре /game 🎮</span>'), 
                sep='\n'
            )
            await callback.message.edit_text(text, parse_mode="HTML")
            return

        text = mk.text(
            mk.text('🎉 Поздравляем с получением приза!'),
            mk.hbold(f"Вы выиграли {result} крышек 🪙")
        )
        await callback.message.edit_text(text, parse_mode="HTML")
    except:
        current_time = datetime.now().strftime('%H:%M %d.%m')
        text = mk.text(
            mk.hbold('⚠️ Обнаружена техническая неполадка'),
            mk.text(f'Пожалуйста, сообщите администратору {settings.ADMIN_USERNAME}'),
            mk.text(f'Скопируйте для отправки: give_box {tg_id} - {current_time}'),
            sep='\n'
        )
        await callback.message.edit_text(text, parse_mode="HTML")


