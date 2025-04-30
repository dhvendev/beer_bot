from aiogram import Router, types, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.enums import ChatType, DiceEmoji
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.other.replies import LINK_BOT, BEER_UNIT
import aiogram.utils.markdown as mk
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bot.db_async import User
from sqlalchemy.ext.asyncio import AsyncSession



router = Router()


class AddChance(StatesGroup):
    count = State()


class CallbackChance(CallbackData, prefix='chance'):
    text: str


@router.message(Command('shop'), F.chat.type != ChatType.PRIVATE)
async def cmd_shop(message: Message) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Перейти в ЛС✌",
        url=LINK_BOT
    ))
    text = mk.text(mk.hbold('Магазин'), "доступен только в лс бота🍺")
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
    return


@router.message(Command('shop'), F.chat.type == ChatType.PRIVATE)
async def cmd_shop(message: Message) -> None:
    text = mk.text('Рад видеть тебя в нашем магазине', mk.hbold('Beer Bot!'), '\nНа данный момент можно купить только лишь:')
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Увеличение шанса 📶', callback_data=CallbackChance(text='add_chance').pack()))
    await message.answer(text, parse_mode='HTML', reply_markup=builder.as_markup())
    return


@router.callback_query(CallbackChance.filter(F.text == 'add_chance'))
async def call_add_chance(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    text = mk.hbold('Введите какое кол-во шанса которое ты хочешь приобрести.\n\n') + mk.hbold('Цена по курсу:') + mk.text(' 1% шанса = 25 крышек') + mk.hbold('\nПринимается только число!')
    await callback.message.answer(text, parse_mode='HTML')
    await state.set_state(AddChance.count)


@router.message(AddChance.count)
async def chance(message: Message, state: FSMContext, session: AsyncSession, user: User):
    count = message.text
    await state.clear()
    try:
        count = int(count)
        money = 25 * count
        if user.money < money:
            text = mk.hbold('Недостаточно пивных крышек!') + f"\nНа вашем балансе: " + mk.hbold(str(user.money), "крышек." + '\nЧтобы попробовать снова, воспользуйтесь /shop')
            await message.answer(text, parse_mode='HTML')
            return
        user.money -= money
        user.chance += count
        await session.commit()
        text = mk.hbold('Успешно!') + f'\nВаш шанс изменился с {user.chance - count} на {user.chance}' + f"\nНа вашем балансе: " + mk.hbold(str(user.money), "крышек.")
        await message.answer(text, parse_mode='HTML')
        return
    except ValueError:
        await session.rollback()
        await message.answer(mk.text('Вводить требуется только число!', '\nЧтобы попробовать снова, воспользуйтесь /shop'), parse_mode='HTML')


