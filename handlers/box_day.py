from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, InlineKeyboardButton
from aiogram.enums import ChatType, ChatMemberStatus
from aiogram.utils.keyboard import InlineKeyboardBuilder

import bot.db_async
from bot.other.replies import LINK_BOT, ID_CHAT, ID_NEWS, LINK_NEWS, LINK_CHAT
import aiogram.utils.markdown as mk
from bot.db_async import check_ban
import random

#Подсчет результата
def get_random_prize() -> int:
    random_number = random.randint(0, 99)
    if random_number < 40: return 5
    elif random_number < 65: return 10
    elif random_number < 85: return 20
    elif random_number < 95: return 30
    else: return 50


class CallbackBox(CallbackData, prefix='box_day'):
    text: str


router = Router()


@router.message(Command('day'))
async def cmd_day(message: Message, bot: Bot) -> None:
    # Проверяем сообщение на тип чата
    if message.chat.type != ChatType.PRIVATE:  # Проверяем на приватность чат
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Перейти в ЛС✌",
            url=LINK_BOT
        ))
        text = mk.text(mk.hbold('Ежедневные коробки'), "доступны только в лс бота🍺")
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
        return
    tg_id = message.from_user.id

    # Проверяем подписку на NEWS
    check_subscribe = await bot.get_chat_member(ID_NEWS, tg_id)
    if check_subscribe.status == ChatMemberStatus.LEFT or check_subscribe.status == ChatMemberStatus.KICKED:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Наш новостной канал🍺",
            url=LINK_NEWS
        ))
        text = mk.text(mk.hbold('Отсутствует подписка на новостной канал😔'))
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
        return

        # Проверяем подписку на CHAT
    check_subscribe = await bot.get_chat_member(ID_CHAT, tg_id)
    if check_subscribe.status == ChatMemberStatus.LEFT or check_subscribe.status == ChatMemberStatus.KICKED:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Наш общий чат🍺",
            url=LINK_CHAT
        ))
        text = mk.text(mk.hbold('Отсутствует подписка на общий чат😔'))
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
        return
    name = message.from_user.first_name or "unknown"
    link = message.from_user.username or "unknown"

    # Проверяем не заблокирован ли пользователь
    ban = await check_ban(tg_id, name, link, '/day')
    if ban:
        expiration_time = ban.expiration
        text = mk.text(
            mk.hbold('Вы заблокированы в системе получения призов!'),
            mk.text('Блокировка до:', mk.hbold(expiration_time.strftime("%d.%m.%Y %H:%M"))),
            mk.text('Если вы считаете, что блокировка была выдана случайно, сообщите @plymdvev'),
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
    try:
        tg_id = callback.from_user.id
        name = callback.from_user.first_name or "unknown"
        link = callback.from_user.username or "unknown"
        result = get_random_prize()  # Считаем результат

        user, status = await bot.db_async.box(tg_id, name, link, result)
        if not status:
            text = mk.text(
                mk.hbold(f"Ты уже забрал(а) свой приз {user.created.strftime('%d.%m.%y')} в {user.created.strftime('%H:%M')}✌️"),
                mk.text('Приходи завтра!'),
                mk.text(f'<span class="tg-spoiler">А пока можешь поиграть в /game </span>'), sep='\n'
            )
            await callback.message.edit_text(text, parse_mode="HTML")
            return
        text = mk.text(
            mk.text('Вам выпало:'),
            mk.hbold(result, 'крышек.')
        )
        await callback.message.edit_text(text, parse_mode="HTML")
    except:
        text = mk.text(
            mk.hbold('Ошибка!'),
            mk.text('Сообщите @plymvdev, шаблон сообщения: ТУТ БУДЕТ ССЫЛКА'),
            sep='\n'
        )
        await callback.message.edit_text(text, parse_mode="HTML")


