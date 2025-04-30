import asyncio
import logging, random
import os
import glob
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from handlers import start, members, drink, tops, box_day, games, admin, me, shop
from aiogram.fsm.storage.memory import MemoryStorage
from middlewares.db import DbSessionAndCheckRegister
import aiocron
from core.db_async import reset_count
import json
from core.config import settings

current_dir = os.getcwd()
config_path = os.path.join(current_dir, 'config.json')
logs_dir = os.path.join(current_dir, 'logs')


if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

def setup_logging():
    """Настройка логирования с хранением логов по датам"""
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(logs_dir, f'log_{current_date}.log')
    

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        filename=log_file,
        filemode="a"
    )
    
    cleanup_old_logs()

def cleanup_old_logs():
    """Удаление логов старше 7 дней"""
    current_date = datetime.now()
    retention_days = 7
    
    # Получаем все файлы логов
    log_files = glob.glob(os.path.join(logs_dir, 'log_*.log'))
    
    for log_file in log_files:
        try:

            filename = os.path.basename(log_file)
            date_str = filename.replace('log_', '').replace('.log', '')
            file_date = datetime.strptime(date_str, '%Y-%m-%d')
            

            if (current_date - file_date).days > retention_days:
                os.remove(log_file)
                logging.info(f"Удален устаревший лог: {filename}")
        except Exception as e:
            logging.error(f"Ошибка при обработке файла лога {log_file}: {e}")

async def reset_status_count(bot: Bot):
    result = await reset_count()
    await bot.send_message(5779074567, f'Сброс {datetime.now()}')


async def test(bot: Bot):
    await bot.send_message(5779074567, f'Тест {datetime.now()}')


async def reset_factor_day(bot: Bot):
    with open(config_path) as f:
        config = json.load(f)
    old_factor = config["FACTOR_DAY"]
    config["FACTOR_DAY"] = random.randint(30, 90)
    with open(config_path, 'w') as f:
        json.dump(config, f)
    await bot.send_message(5779074567, f'Коэффициент изменен с {old_factor} на {config["FACTOR_DAY"]}')


async def main():
    print('START BOT')
    # Настраиваем логирование перед запуском бота
    setup_logging()
    logging.info("bot started")
    
    bot = Bot(token=settings.TOKEN)
    aiocron.crontab("0 0 * * *", func=reset_status_count, args=(bot,)).start()
    aiocron.crontab("0 12 * * *", func=reset_status_count, args=(bot,)).start()
    aiocron.crontab("0 0 * * *", func=reset_factor_day, args=(bot,)).start()
    
    # Добавляем ежедневное обновление файла логов
    aiocron.crontab("1 0 * * *", func=lambda: setup_logging()).start()
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    #Подключение мидлвар ( на каждый отклик проверяем регистрацию и передаем созданную сессию)
    dp.message.middleware(DbSessionAndCheckRegister()) 

    #Подключение:
    dp.include_router(games.router) #/clear и /game
    dp.include_router(shop.router) #/shop                       WORK not keyboard
    dp.include_router(admin.router) #/factor и /factor_edit
    dp.include_router(tops.router)  #/top и /fulltop            WORK not keyboard
    dp.include_router(drink.router) #/drink
    
    #Исправленные:
    dp.include_router(box_day.router) #/day
    dp.include_router(start.router) #/start и /help
    dp.include_router(me.router) #/me
    dp.include_router(members.router) #check left member from chat

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    asyncio.run(main())