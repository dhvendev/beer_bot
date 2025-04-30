from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import Message
import aiogram.utils.markdown as mk
import json
from main import config_path


router = Router()


#Просмотр коэффициента дня
@router.message(Command('factor'))
async def cmd_factor(message: Message):
    with open(config_path) as f:
        config = json.load(f)
    await message.answer(mk.text(config["FACTOR_DAY"], '😂'))
    return


#Изменение коэффициента дня
@router.message(Command('factor_edit'))
async def cmd_factor(message: Message):
    factor = message.text.split(' ')
    if len(factor) == 1:
        await message.answer(mk.text('Недостаточно аргументов для изменения \"КОЭФИЦЕНТА ДНЯ\"', 'Пример: ', mk.hcode('/factor_edit 50')), parse_mode='HTML')
        return
    factor = factor[-1]
    try:
        with open(config_path) as f:
            config = json.load(f)
        old_factor = config["FACTOR_DAY"]
        config["FACTOR_DAY"] = factor
        with open(config_path, 'w') as f:
            json.dump(config, f)
        await message.answer(mk.text(f'Коэффициент изменен с {old_factor} на {factor}'), parse_mode='HTML')
        return
    except ValueError:
        await message.answer(
            mk.text('Аргумент должен быть числом!', 'Пример: ', mk.hcode('/factor_edit 50')), parse_mode='HTML')
        return


