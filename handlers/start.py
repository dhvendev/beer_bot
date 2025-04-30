from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton
from aiogram.enums import ChatType
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.other.replies import LINK_BOT
import aiogram.utils.markdown as mk
from sqlalchemy.ext.asyncio import AsyncSession
from bot.other.replies import LINK_NEWS, LINK_CHAT

router = Router()


@router.message(Command('start'), F.chat.type == ChatType.PRIVATE)
async def cmd_start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='Добавить в группу🍺✌️',
        url=f'{LINK_BOT}?startgroup=true'))
    text = mk.text(
        mk.text(mk.hbold('Доброго времени суток!\n')),
        mk.text("Я бот для чатов \"Beer Bot\""),
        mk.text(mk.hbold("В чем суть?")),
        mk.text("📌 1 раз в сутки каждый участник чата обладает возможностью использовать команду выпить,"
                " на что получит случайное число  от -3.5 до +5 л."),
        mk.text("📌 В дополнение, также существуют ряд команд с которыми можно ознакомиться по команде: /help"),
        mk.text("📌 По партнерстве и рекламе: @plymvdev"),
        mk.hbold("Важно!"),
        mk.text("Цель создания этого бота - исключительно развлекательная. Важно отметить, что функция 'выпить'"
                " в данном боте является вымышленной и не призывает к реальному потреблению напитков. Также, функция"
                " 'game' не пропагандирует азартные игры, а служит лишь развлекательной цели"),
        sep='\n')
    await message.answer(text, parse_mode='HTML', reply_markup=builder.as_markup())
    return


@router.message(Command('start'), F.chat.type != ChatType.PRIVATE)
async def cmd_start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Перейти в ЛС✌️",
        url=LINK_BOT))
    text = mk.text(
        mk.text(mk.hbold('Бот добавлен!')),
        mk.text("Приятного использования🍺"),
        mk.text("<span class='tg-spoiler'>Ознакомься с другими крутыми командами в лс</span>"),
        sep='\n')
    await message.answer(text, parse_mode='HTML', reply_markup=builder.as_markup())
    return


@router.message(Command('help'))
async def cmd_help(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='📰 Новостной канал бота', url=LINK_NEWS))
    builder.row(InlineKeyboardButton(text='💬 Общий чат с ботом', url=LINK_CHAT))
    text = mk.text(
        mk.hbold('Актуальные команды бота:'),
        mk.text("/start, /help - приветствие и помощь"),
        mk.hbold('Команды только в \"ЛС\" бота:'),
        mk.text("/day - ежедневные коробки удачи"),
        mk.text("/game - мини игра на крышки"),
        mk.text("/fulltop - глобальный топ"),
        mk.text("/shop - магазин бота"),

        mk.hbold('Команды только в \"Чатах и группах\" :'),
        mk.text("/drink - выпить"),
        mk.text("/top - местный топ"),

        mk.hbold('Общие команды:'),
        mk.text("/me - о тебе"),
        sep='\n'
    )
    return await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
