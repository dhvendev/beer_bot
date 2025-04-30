from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton
from aiogram.enums import ChatType
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiogram.utils.markdown as mk
from core.config import settings

router = Router()


@router.message(Command('start'), F.chat.type == ChatType.PRIVATE)
async def cmd_start(message: Message):
    """
    Command /start for private chat
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text='🍻 Добавить в группу 🍻',
        url=f'{settings.LINK_BOT}?startgroup=true'))
    builder.row(InlineKeyboardButton(
        text='📱 Наш канал с новостями',
        url=settings.LINK_NEWS))
    
    text = mk.text(
        mk.text(mk.hbold('🍺 Добро пожаловать в Beer Bot! 🍺')),
        mk.text("Превратите ваш групповой чат в веселое соревнование с виртуальными напитками!"),
        
        mk.hbold("\n🎮 Основные функции:"),
        mk.text("🔸 Команда /drink — получайте от -3.5 до +5 литров раз в сутки"),
        mk.text("🔸 Таблица лидеров в каждом чате — выясните, кто настоящий чемпион"),
        mk.text("🔸 Ежедневные коробки удачи — дополнительные бонусы каждый день"),
        mk.text("🔸 Мини-игры на крышки — увеличивайте свой счёт"),
        
        mk.hbold("\n🚀 Начало работы:"),
        mk.text("1️⃣ Добавьте бота в вашу группу с помощью кнопки ниже"),
        mk.text("2️⃣ Используйте команду /drink, чтобы начать соревнование"),
        mk.text("3️⃣ Проверяйте рейтинг с помощью команды /top"),
        mk.text("4️⃣ Откройте все команды с помощью /help"),
        
        mk.hbold("\n📞 Контакты:"),
        mk.text(f"По вопросам сотрудничества: {settings.ADMIN_USERNAME}"),
        
        mk.hbold("\n⚠️ Важное примечание:"),
        mk.text("Бот создан исключительно в развлекательных целях. Функция \"выпить\" является вымышленной и не призывает к реальному потреблению алкоголя. Мини-игры не пропагандируют азартные игры, а служат только для развлечения."),
        sep='\n')
    
    await message.answer(text, parse_mode='HTML', reply_markup=builder.as_markup())
    return


@router.message(Command('start'), F.chat.type != ChatType.PRIVATE)
async def cmd_start(message: Message):
    """
    Command /start for public chat
    """
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Открыть личку 💬",
        url=settings.LINK_BOT))
    text = mk.text(
        mk.text(mk.hbold('🎉 Beer Bot успешно добавлен! 🎉')),
        mk.text("\n💬 Готовы повеселиться?"),
        mk.text("Используйте команду /drink чтобы начать!"),
        mk.text("<span class='tg-spoiler'>🎁 Команды: /game /box и другие, ждут вас в личке</span>"),
        sep='\n')
    await message.answer(text, parse_mode='HTML', reply_markup=builder.as_markup())
    return



@router.message(Command('help'))
async def cmd_help(message: Message):
    """
    Command /help for all types chat
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='📰 Новостной канал бота', url=settings.LINK_NEWS))
    builder.row(InlineKeyboardButton(text='💬 Общий чат с ботом', url=settings.LINK_CHAT))
    text = mk.text(
        mk.hbold('🍺 Команды Beer Bot 🍺'),
        
        mk.hbold('\n🌐 Основные команды:'),
        mk.text("🔹 /start - запустить бота"),
        mk.text("🔹 /help - показать это меню"),
        mk.text("🔹 /me - информация о вашем профиле"),
        
        mk.hbold('\n💬 Команды в личных сообщениях:'),
        mk.text("🎁 /day - получить ежедневную коробку удачи"),
        mk.text("🎮 /game - мини-игра на крышки"),
        mk.text("🏆 /fulltop - глобальный рейтинг игроков"),
        mk.text("🛒 /shop - магазин бота"),
        
        mk.hbold('\n👥 Команды в групповых чатах:'),
        mk.text("🍻 /drink - выпить случайное количество (от -3.5 до +5 л)"),
        mk.text("📊 /top - рейтинг участников в этом чате"),
        
        mk.hbold('\n📱 Полезные ссылки:'),
        mk.text("Больше новостей и обновлений в нашем канале и чате 👇"),
        sep='\n'
    )
    return await message.answer(text, reply_markup=builder.as_markup(), parse_mode='HTML')
