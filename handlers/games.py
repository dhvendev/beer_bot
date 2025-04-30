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
from aiogram.methods import SendDice
from math import ceil
from bot.db_async import game
import json
from .admin import config_path



router = Router()


class Game(StatesGroup):
    id_game = State()
    start = State()
    count = State()
    values = State()
    game = State()

class CallbackGame(CallbackData, prefix='game'):
    text: str


@router.message(Command('clear'))
async def clear(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await message.answer('Все действующие состояния отключены')


@router.message(Command('game'))
async def cmd_game(message: Message, state: FSMContext) -> None:
    if message.chat.type != ChatType.PRIVATE:  # Проверяем на приватность чат
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Перейти в ЛС✌",
            url=LINK_BOT
        ))
        text = mk.text(mk.hbold('Мини игра'), "доступна только в лс бота🍺")
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
        return
    current_state = await state.get_state()
    if current_state:
        await message.answer(mk.text(mk.hbold("Ошибка!"),
                                     mk.hbold("Возможные причины:"),
                                     "- у вас есть незавершенная игра;",
                                     "- вы повторно пытаетесь отправить запрос на игру;",
                                     "- возможно вы жульничаете",
                                     mk.hbold("Решение: /clear"), sep='\n'
                                     ), parse_mode='HTML')
        return
    await state.set_state(Game.start)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Да✅', callback_data=CallbackGame(text='yes').pack()))
    builder.add(InlineKeyboardButton(text='Нет❌', callback_data=CallbackGame(text='no').pack()))
    await message.answer(mk.text(
        mk.hbold('Запуск игры - 10 крышек с баланса.\n'),
        mk.hbold('Важно:'),
        mk.text('После запуска игры, у вас будет 5 попыток прокрутить анимированное сообщение.'),
        mk.text('В случае, если игра будет не завершена, удален чат, попытка одновременного запуска нескольких игр, игра завершится без возврата потраченных крышек'),
        mk.hbold('\nГотов(а) начать игру?'), sep='\n'),
        reply_markup=builder.as_markup(), parse_mode='HTML')


@router.message(StateFilter(Game))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await message.delete()
    current_state = await state.get_state()
    if current_state is None:
        return
    print("Cancelled.")
    await state.clear()
    await message.answer("Cancelled.")


@router.callback_query(CallbackGame.filter(F.text == 'no'))
async def call_yes(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    current_state = await state.get_state()
    if current_state is None:
        return
    print("Cancelled.")
    await state.clear()


@router.callback_query(CallbackGame.filter(F.text == 'yes'))
async def call_yes(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    tg_id = callback.from_user.id
    name = callback.from_user.first_name or "unknown"
    link = callback.from_user.username or "unknown"
    user, status, id_game = await game(tg_id, name, link, -10)
    if not status:
        await callback.message.answer(
            mk.text("Упс, ваших крышек не хватает на запуск игры😔\n", "Крышек на балансе:", mk.hbold(user.money)),
            parse_mode='HTML')
        return
    print('id записи игры: ', id_game)
    await state.update_data(count=5, id_game=id_game)
    await state.set_state(Game.game)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Играть', callback_data=CallbackGame(text='play').pack()))
    await callback.message.answer(mk.text(
        mk.hbold('Игра запущена!'),
        'Нажимай на кнопку, чтобы играть',
        'У тебя осталось 5 попыток'),
        reply_markup=builder.as_markup(), parse_mode='HTML'
    )


@router.callback_query(CallbackGame.filter(F.text == 'play'))
async def call_play(callback: CallbackQuery, state: FSMContext, bot: Bot):
    current_state = await state.get_state()
    if current_state is None:
        await callback.message.delete()
        return
    data = await state.get_data()
    count = data.get('count')
    values = data.get('values', {})
    new_count = count-1
    if new_count < 0:
        id_game = data.get('id_game')
        await state.clear()
        collect = await callback.message.edit_text('Идет подсчет результатов..')
        result, text = await check_result(values)
        await collect.edit_text(text, parse_mode='HTML')
        tg_id = callback.from_user.id
        name = callback.from_user.first_name or "unknown"
        link = callback.from_user.username or "unknown"
        await game(tg_id, name, link, result, True, id_game)
        return
    builder = InlineKeyboardBuilder()
    TEXT_BUTTON = f'Играть'
    TEXT_MSG = f'Давай еще, у тебя осталось: {new_count} попыток✌️'
    if new_count == 0:
        TEXT_BUTTON = f'Забрать выигрыш🎁'
        TEXT_MSG = 'Кликай и забирай свой выигрыш✌️'
    builder.add(InlineKeyboardButton(text=TEXT_BUTTON, callback_data=CallbackGame(text='play').pack()))
    await state.update_data(count=count - 1, values=values)
    try:
        await callback.message.delete()
        slot_message = await bot.send_dice(callback.message.chat.id, emoji=DiceEmoji.SLOT_MACHINE)
        values[count] = slot_message.dice.value
        await bot.send_message(callback.message.chat.id, TEXT_MSG, reply_markup=builder.as_markup())
    except:
        await bot.send_message(callback.message.chat.id, mk.text(
            mk.hbold('Замечено жульничество!'),
            mk.text('При нажатии играть, дождитесь результата. ')
        ), parse_mode='HTML')


async def check_result(results: dict):
    result = 0
    text = mk.hbold('Результаты игры:')
    for key, value in enumerate(results.values()):
        if value in [5, 9, 13]:
            mid_result = 2
            COMB = "🍫❌🍫"
        elif value in [18, 26, 30]:
            mid_result = 3
            COMB = "🍇❌🍇"
        elif value in [35, 39, 47]:
            mid_result = 4
            COMB = "🍋❌🍋"
        elif value in [52, 56, 60]:
            mid_result = 5
            COMB = "7️⃣❌7️⃣"
        elif value == 1:
            mid_result = 8
            COMB = "🍫🍫🍫"
        elif value == 22:
            mid_result = 12
            COMB = "🍇🍇🍇"
        elif value == 43:
            mid_result = 15
            COMB = "🍋🍋🍋"
        elif value == 64:
            mid_result = 20
            COMB = "7️⃣7️⃣7️⃣"
        else:
            mid_result = 0
            COMB = "❌❌❌"
        result += mid_result
        text += f"\n{key+1}. +{mid_result} - {COMB}"
    with open(config_path) as f:
        config = json.load(f)
    factor = int(config["FACTOR_DAY"])
    result *= (1 + (factor / 100))
    result = ceil(result)
    text += mk.hbold('\n\nИтого:') + mk.text('\nС учетом коэффициента дня: + ') + mk.hbold(f'{factor}%') + mk.text('\nНа ваш баланс зачислено: ') + mk.hbold(result)
    return result, text

