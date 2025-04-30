import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from db_async import async_session, User, Chat, CountDrink
from sqlalchemy import Integer, BigInteger, Column, String, DateTime, Float, ForeignKey, MetaData, select, \
    create_engine, desc, Boolean, func

import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def select_chat(self):
        with self.connection:
            result = self.cursor.execute("SELECT * from `chat`").fetchall()
            return result

    def select_user(self):
        with self.connection:
            result = self.cursor.execute("SELECT DISTINCT tg_user_id, tg_name, tg_link FROM user").fetchall()
            return result

    def update_money(self):
        with self.connection:
            result = self.cursor.execute("SELECT balance.user_id, balance.count FROM balance WHERE balance.count != 0").fetchall()
            return result

    def count(self):
        with self.connection:
            result = self.cursor.execute("SELECT user.tg_user_id, user.tg_chat_id, user.count_pivo FROM user").fetchall()
            return result


db = Database('base102.db')


async def add_chat():
    async with async_session() as session:
        chats = db.select_chat()
        for i in chats:
            chat_id = i[1]
            name = i[2]
            chat = Chat(chat_id=chat_id,
                        name=name)
            session.add(chat)

        await session.commit()
        return True


async def add_user():
    async with async_session() as session:
        users = db.select_user()
        for i in users:
            tg_id = i[0]
            name = i[1]
            link = i[2]
            result = await session.execute(select(User).where(User.tg_id == tg_id))
            bd_user = result.scalars().first()
            if bd_user is None:
                user = User(tg_id=tg_id,
                            name=name,
                            link=link)
                session.add(user)

        await session.commit()
        return True


async def edit_money():
    users = db.update_money()
    async with async_session() as session:
        for i in users:
            result = await session.execute(select(User).where(User.tg_id == i[0]))
            user = result.scalars().first()
            if user:
                user.money += i[1]
            else:
                print('Error', i)
        await session.commit()


async def add_count():
    users = db.count()
    async with async_session() as session:
        for i in users:
            try:
                user_id = i[0]
                chat_id = i[1]
                count = i[2]
                user = await session.execute(select(User).where(User.tg_id == user_id))
                user_obj = user.scalars().first()
                chat = await session.execute(select(Chat).where(Chat.chat_id == chat_id))
                chat_obj = chat.scalars().first()
                count_drink = CountDrink(user=user_obj, chat=chat_obj, count=count, status=False)
                session.add(count_drink)
            except Exception as e:
                print('!!! error', e, user_id, chat_id)
        await session.commit()





async def main():
    result = await add_chat()
    print(result)
    result = await add_user()
    print(result)
    result = await edit_money()
    print(result)
    result = await add_count()
    print(result)

asyncio.run(main())


