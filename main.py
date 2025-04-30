import asyncio
import logging, random
from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv
from handlers import start, members, drink, tops, box_day, games, admin, me, shop
from aiogram.fsm.storage.memory import MemoryStorage
from middlewares.db import DbSessionAndCheckRegister
import aiocron
from bot.db_async import reset_count
import sys
from datetime import datetime
import json

load_dotenv('.env')
current_dir = os.getcwd()
config_path = os.path.join(current_dir, 'config.json')



async def reset(bot: Bot):
    result = await reset_count()
    await bot.send_message(5779074567, f'Сброс {datetime.now()}')


async def test(bot: Bot):
    await bot.send_message(5779074567, f'Тест {datetime.now()}')


async def reset_koef(bot: Bot):
    with open(config_path) as f:
        config = json.load(f)
    old_factor = config["FACTOR_DAY"]
    config["FACTOR_DAY"] = random.randint(30, 90)
    with open(config_path, 'w') as f:
        json.dump(config, f)
    await bot.send_message(5779074567, f'Коэффициент изменен с {old_factor} на {config["FACTOR_DAY"]}')


async def main():


    print('START BOT')
    bot = Bot(token=os.environ.get('TOKEN'))
    aiocron.crontab("0 0 * * *", func=reset, args=(bot,)).start()
    aiocron.crontab("0 12 * * *", func=reset, args=(bot,)).start()
    #aiocron.crontab("0 18 * * *", func=reset, args=(bot,)).start()
    #aiocron.crontab("0 22 * * *", func=reset, args=(bot,)).start()
    aiocron.crontab("0 0 * * *", func=reset_koef, args=(bot,)).start()
    #aiocron.crontab("*/1 * * * *", func=test, args=(bot,)).start()
    #bot = Bot(token='6014743395:AAGpv-5gXw_810WtS0rti-5kBizejHREQJw')
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.message.middleware(DbSessionAndCheckRegister()) #Проверяем регистрацию и делаем сессию

    #Подключение:
    dp.include_router(games.router) #/clear и /game
    dp.include_router(shop.router) #/shop                       WORK not keyboard
    dp.include_router(admin.router) #/factor и /factor_edit

    dp.include_router(start.router) #/start и /help             WORK not keyboard
    dp.include_router(tops.router)  #/top и /fulltop            WORK not keyboard

    dp.include_router(box_day.router) #/day
    dp.include_router(drink.router) #/drink
    dp.include_router(me.router) #/me                           WORK

    dp.include_router(members.router)

    #dp.include_router(test.router)







    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        filename="logs.log",
        filemode="a"
    )
    asyncio.run(main())
