import asyncio
from datetime import datetime, timedelta, date
from sqlalchemy import Integer, BigInteger, Column, String, DateTime, Float, ForeignKey, MetaData, select, \
    create_engine, desc, Boolean, func, update, values
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from bot.other.other_func import generate_random_number
from typing import Union, Tuple, Any
from core.config import settings

engine = create_async_engine(
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
    echo=False)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, nullable=False, unique=True)
    name = Column(String, nullable=False)
    link = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.now)
    chance = Column(Integer, default=45)
    money = Column(Integer, default=100)


class Chat(Base):
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)
    name = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.now)


class CountDrink(Base):
    __tablename__ = 'count_drink'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    chat_id = Column(BigInteger, ForeignKey('chat.id'))
    count = Column(Float, default=0.0, nullable=False)
    status = Column(Boolean, default=False, nullable=False)
    user = relationship('User', backref='chats')
    chat = relationship('Chat', backref='users')


class CommandHistory(Base):
    __tablename__ = 'cmd_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    chat_id = Column(BigInteger, ForeignKey('chat.id'))
    name = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.now)
    user = relationship('User', backref='cmd_history_user')
    chat = relationship('Chat', backref='cmd_history_chat')


class BanUser(Base):
    __tablename__ = 'ban_user'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    command = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.now, nullable=False)
    expiration = Column(DateTime, nullable=False)
    user = relationship('User', backref='ban_users')


class GamesHistory(Base):
    __tablename__ = 'games_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    status = Column(Boolean, default=False, nullable=False)
    prize = Column(Integer, default=None)
    created = Column(DateTime, default=datetime.now, nullable=False)
    user = relationship('User', backref='games_history_user')


class BoxHistory(Base):
    __tablename__ = 'box_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    prize = Column(Integer, default=None)
    created = Column(DateTime, default=datetime.now, nullable=False)
    user = relationship('User', backref='box_history_user')

async def get_or_add_user(session, tg_id: int, name: str, link: str):
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalars().first()
    if user is None:
        # Если пользователь не существует, создаем новую запись в таблице User
        user = User(tg_id=tg_id,
                    name=name,
                    link=link)
        session.add(user)
        await session.commit()
    # Обновляем данные если они отличаются с базой:
    if user.name != name: user.name = name
    if user.link != name: user.link = link
    await session.commit()
    return user


async def get_or_add_chat(session, chat_id: int, name: str):
    # Проверяем, существует ли чат в таблице Chat
    result = await session.execute(select(Chat).where(Chat.chat_id == chat_id))
    chat = result.scalars().first()
    if chat is None:
        # Если чат не существует, создаем новую запись в таблице Chat
        chat = Chat(chat_id=chat_id,
                    name=name)
        session.add(chat)
        await session.commit()
    return chat


async def get_or_add_count_drink(session, user: object, chat: object):
    # Создаем запись в таблице UserChat с начальным балансом монет (0)
    result = await session.execute(
        select(CountDrink).options(selectinload(CountDrink.user), selectinload(CountDrink.chat)).where(
            CountDrink.user_id == user.id, CountDrink.chat_id == chat.id))
    count_drink = result.scalars().first()
    if count_drink is None:
        count_drink = CountDrink(user=user, chat=chat, count=0, status=False)
        session.add(count_drink)
        await session.commit()
    return count_drink


async def add_cmd_in_history(session, user: object, chat: object, cmd: str):
    # Создаем запись в таблице CommandHistory записываем использованную команду
    command = CommandHistory(
        user_id=user.id,
        chat_id=chat.id,
        name=cmd
    )
    session.add(command)
    await session.commit()
    return


async def update_count_drink(tg_id: int, chat_id: int, name: str, link: str, chat_title: str):
    """
    :param chat_title: название чата с телеграм
    :param link: username полученный с телеграм
    :param name: first_name полученный с телеграм
    :param chat_id: id чата полученный с телеграм
    :param tg_id: id пользователя полученный с телеграм
    """
    async with async_session() as session:
        user = await get_or_add_user(session, tg_id, name, link)
        chat = await get_or_add_chat(session, chat_id, chat_title)
        count_drink = await get_or_add_count_drink(session, user, chat)
        if count_drink.status == False:
            update_count_number = generate_random_number(user.chance)
            count_drink.count += update_count_number
            count_drink.status = True
            await session.commit()
        else:
            update_count_number = None

        result = await session.execute(
            select(CountDrink).where(CountDrink.chat_id == chat.id).order_by(desc(CountDrink.count)))
        list_gamer = result.all()
        await add_cmd_in_history(session, user, chat, '/drink')

        return count_drink, list_gamer, update_count_number


async def get_top_local(tg_id: int, chat_id: int, name: str, link: str, chat_title: str):
    """
    :param chat_title: название чата с телеграм
    :param link: username полученный с телеграм
    :param name: first_name полученный с телеграм
    :param chat_id: id чата полученный с телеграм
    :param tg_id: id пользователя полученный с телеграм
    """
    async with async_session() as session:
        user = await get_or_add_user(session, tg_id, name, link)
        chat = await get_or_add_chat(session, chat_id, chat_title)

        result = await session.execute(
            select(User, CountDrink).join(User).where(CountDrink.chat_id == chat.id).order_by(
                desc(CountDrink.count)).limit(15))
        list_gamer = result.all()
        await add_cmd_in_history(session, user, chat, '/top')
        return list_gamer


async def get_top_global(tg_id: int, chat_id: int, name: str, link: str, chat_title: str):
    """
    :param chat_title: название чата с телеграм
    :param link: username полученный с телеграм
    :param name: first_name полученный с телеграм
    :param chat_id: id чата полученный с телеграм
    :param tg_id: id пользователя полученный с телеграм
    """
    async with async_session() as session:
        user = await get_or_add_user(session, tg_id, name, link)
        chat = await get_or_add_chat(session, chat_id, chat_title)

        result = await session.execute(
            select(User, CountDrink).join(User).order_by(desc(CountDrink.count)).limit(15))
        list_gamer = result.all()
        await add_cmd_in_history(session, user, chat, '/fulltop')
        return list_gamer


async def check_ban(tg_id: int, name: str, link: str, cmd: str) -> Union[None, BanUser]:
    """

    """
    async with async_session() as session:
        user = await get_or_add_user(session, tg_id, name, link)

        result = await session.execute(
            select(BanUser).
            where(BanUser.user_id == user.id, BanUser.command == cmd, BanUser.expiration > datetime.now())
        )
        result = result.scalars().first()
        if not result: return None
        return result


async def get_user(session, tg_id: int) -> Union[None, User]:
    """
    Возвращает пользователя с базы по tg_id
    :param session: открытая сессия
    :param tg_id: пользователя с тг
    :return:
    """
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalars().first()
    if user is None:
        return None
    return user


async def give_ban(tg_id: int, cmd: str, day: int) -> Union[None, BanUser]:
    """
    :param tg_id: id пользователя полученный с телеграм
    :param cmd: заблокированная команда
    :param day: кол-во дней блокировки
    """
    async with async_session() as session:
        user = await get_user(session, tg_id)
        if not user: return None  # Возвращаем если пользователь не играл ниразу
        result = await session.execute(
            select(BanUser).
            where(
                BanUser.user_id == user.id,
                BanUser.command == cmd,
                BanUser.expiration > datetime.now()
            )
        )
        ban_user = result.scalars().first()
        if ban_user is None:
            ban_user = BanUser(
                user_id=user.id,
                command=cmd,
                expiration=datetime.now()
            )
        ban_user.expiration += timedelta(days=day)
        session.add(ban_user)
        await session.commit()
        return ban_user


#Не требуеющие изменений.
# Получение или изменение кол-во монет у пользователя
async def get_or_edit_money(tg_id: int, name: str, link: str, money=0) -> tuple[User, bool]:
    """
    Возвращается кол-во монет, может использоваться как изменение баланса пользователя.
    :param tg_id: id пользователя полученный с телеграм
    :param name: first_name полученный с телеграм
    :param link: username полученный с телеграм
    :param money: кол-во монет у пользователя
    """
    async with async_session() as session:
        user = await get_or_add_user(session, tg_id, name, link)
        if money != 0:
            delta_money = user.money + money
            if delta_money < 0:
                return user, False
            user.money = delta_money
            await session.commit()
        return user, True


# Добавление игры в базу данных, start и finish
async def game(tg_id: int, name: str, link: str, money:int, status=False, id_game=None) -> tuple[User, bool, GamesHistory.id or None]:
    """
    Возвращается кол-во монет, может использоваться как изменение баланса пользователя.

    :param id_game: id в базе
    :param tg_id: id пользователя полученный с телеграм
    :param name: first_name полученный с телеграм
    :param link: username полученный с телеграм
    :param money: кол-во монет у пользователя
    :param status: True  - игра закончена, False and money>0 - Игра начинается
    """
    async with async_session() as session:
        user = await get_or_add_user(session, tg_id, name, link)
        if not status: #Игра запускается
            delta_money = user.money + money
            if delta_money < 0:
                return user, False, None
            user.money = delta_money
            game = GamesHistory(user_id=user.id)
            session.add(game)
            await session.commit()
            return user, True, game.id
        result = await session.execute(select(GamesHistory).where(GamesHistory.id == id_game))
        game = result.scalars().first()
        if game is None: return
        game.status = True
        game.prize = money
        user.money += money
        await session.commit()
        return game.id



async def box(tg_id: int, name: str, link: str, money: int) -> tuple[BoxHistory, bool]:
    async with async_session() as session:
        user = await get_or_add_user(session, tg_id, name, link)
        result = await session.execute(
            select(BoxHistory).where(BoxHistory.user_id == user.id,
                                     func.date(BoxHistory.created) == datetime.now().date())
        )
        opened_box = result.scalars().first()
        if opened_box:
            return opened_box, False
        opened_box = BoxHistory(user_id=user.id, prize=money)
        user.money += money
        session.add(opened_box)
        await session.commit()
        return opened_box, True


async def give_money(session, tg_id):
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalars().first()
    if user:
        user.money += 500
    await session.commit()
    return user


#Переделанные

async def get_top(session: AsyncSession, user: User, chat: Chat) -> list:
    """
    Получаем список топа в данном чате с лимитом на 15 игроков.
    """
    result = await session.execute(
        select(User, CountDrink).join(User).where(CountDrink.chat_id == chat.id).order_by(
            desc(CountDrink.count)).limit(15))
    list_gamer = result.all()
    await add_cmd_in_history(session, user, chat, '/top')
    return list_gamer


async def get_fulltop(session: AsyncSession) -> list:
    """
    Получаем список топа со всех чатов с лимитом на 15 игроков.
    """
    result = await session.execute(
        select(User, CountDrink).join(User).order_by(desc(CountDrink.count)).limit(15))
    list_gamer = result.all()
    return list_gamer


async def update_drink(session: AsyncSession, user: User, chat: Chat):
    """
    """
    count_drink = await get_or_add_count_drink(session, user, chat)
    if count_drink.status == False:
        update_count_number = generate_random_number(user.chance)
        count_drink.count += update_count_number
        count_drink.status = True
        await session.commit()
    else:
        update_count_number = None

    result = await session.execute(
        select(CountDrink).where(CountDrink.chat_id == chat.id).order_by(desc(CountDrink.count)))
    list_gamer = result.all()
    await add_cmd_in_history(session, user, chat, '/drink')

    return count_drink, list_gamer, update_count_number


async def reset_count():
    async with async_session() as session:
        result = await session.execute(
            update(CountDrink).values(status=False))
        await session.commit()
        return result