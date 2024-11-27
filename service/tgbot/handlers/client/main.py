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
from service.tgbot.keyboards.client.faq import get_faq_btns_new
from service.tgbot.data.faq import faq_texts2
from service.tgbot.misc.states.client import FaqState


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
    text = (f"{gender} {user.name}, вас приветствует команда Qazaq Republic!🤗\n"
            f"Құрметті {user.name}, Сізбен бірге Qazaq Republic командасы!")
    btns, items = await get_faq_btns_new(faq_texts2)
    await message.answer(
        text=text,
        reply_markup=await main_btns()
    )
    await message.answer(
        text="Чем могу помочь? Выберите одну из опций:\nСізге қандай көмек көрсете аламыз? Опциялардың бірін таңдаңыз:",
        reply_markup=btns
    )

    await state.update_data(items=items)
    await FaqState.start.set()


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
    res = 0
    res, msg = await get_balance(
        user=user,
        bot=message.bot
    )
    await message.delete()
    if res == 0:
        await message.answer(
            text="У вас пока нет накопленных бонусов. "
                 "Совершайте покупки и участвуйте в наших акциях, "
                 "чтобы начать зарабатывать баллы!"
        )
    else:
        await message.answer(
            text=f"У вас: {res} бонусов {msg}",
        )
