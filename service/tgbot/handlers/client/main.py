import os
import segno
import datetime

from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import Client
from service.tgbot.keyboards.client.client import main_btns
from service.tgbot.modules.OneС.Function_1C import get_balance
from service.tgbot.misc.delete import remove


async def start_handler(
        message: Message,
        user: Client,
        state: FSMContext
):
    await state.finish()
    await remove(message, 1)
    await remove(message, 0)
    gender = 'Дорогой'
    if user.gender == b'M':
        gender = 'Дорогой'
    elif user.gender == b'F':
        gender = 'Дорогая'
    text = f"{gender} {user.name}, вас приветствует команда Qazaq Republic! Желаем приятных покупок. 🤗"
    await message.answer(
        text=text,
        reply_markup=await main_btns()
    )


async def get_my_qr_handler(
        message: Message,
        user: Client,
        state: FSMContext
):
    await state.finish()
    text = "Ваш QR"

    qrcode = segno.make(user.phone_number, micro=False)

    qrcode.save(user.phone_number + ".png", border=4, scale=7)

    await message.delete()
    await message.answer_photo(
        photo=open(user.phone_number + ".png", "rb"),
        caption=text,
    )
    try:
        os.remove(user.phone_number + ".png")
    except:
        pass


async def get_my_bonus_handler(
        message: Message,
        user: Client,
        state: FSMContext
):
    await state.finish()
    res, msg = await get_balance(
        user=user,
        bot=message.bot
    )
    await message.delete()
    await message.answer(
        text=f"У вас: {res} бонусов {msg}",
    )
