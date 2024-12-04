import os
import segno
import datetime

from aiogram.types.message import Message, ContentTypes
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import ParseMode
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import User
from service.tgbot.keyboards.staff import staff as user_key
from service.tgbot.misc.delete import remove
from service.tgbot.misc.staff.show_purchases import show_purchases


async def purchases_handler(
        message: Message,
        state: FSMContext
):
    await state.finish()
    await remove(message, 0)
    await message.answer(
        text="Выберите:",
        reply_markup=await user_key.choice_staff_btns()
    )


async def all_purchases_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        callback_data: dict,
        state: FSMContext
):
    try:
        await callback.message.delete()
    except:
        pass
    texts = await show_purchases(
        session=session,
        user_id=callback.from_user.id
    )
    if texts:
        for text in texts:
            await callback.message.answer(
                text=text,
                parse_mode=ParseMode.HTML
            )
    else:
        await callback.message.answer(
            text="Вы пока не совершали покупки"
        )


async def purchases_by_date_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        callback_data: dict,
        state: FSMContext
):
    try:
        await callback.message.delete()
    except:
        pass
    texts = await show_purchases(
        session=session,
        date=datetime.datetime.now(),
        user_id=callback.from_user.id
    )
    if texts:
        for text in texts:
            await callback.message.answer(
                text=text,
                parse_mode=ParseMode.HTML
            )
    else:
        await callback.message.answer(
            text="Вы пока не совершали покупки за этот месяц"
        )


async def qr_handler(
        message: Message,
        user: User,
        state: FSMContext
):
    text = "Ваш QR"

    qrcode = segno.make(user.phone_number, micro=False)

    qrcode.save(user.phone_number + ".png", border=4, scale=7)

    await remove(message, 0)
    await message.answer_photo(
        photo=open(user.phone_number + ".png", "rb"),
        caption=text,
    )
    try:
        os.remove(user.phone_number + ".png")
    except:
        pass


async def choice_instruction_handler(
        message: Message,
        user: User,
        state: FSMContext
):
    text = "Выберите на каком языке хотите получить инструкцию"

    await remove(message, 0)
    await message.answer(
        text=text,
        reply_markup=await user_key.instruction_staff_btns()
    )


async def get_instruction_handler(
        callback: CallbackQuery,
        user: User,
        state: FSMContext,
        callback_data: dict
):
    choice = callback_data.get('choice')
    text = {
        'rus': {'text': "Инструкция на русском", 'filename': "QR staff bot_ru.docx"},
        'kaz': {'text': "Инструкция на казахском", 'filename': "QR staff bot_kz.docx"}
    }

    await callback.message.answer_document(
        document=open(text.get(choice).get('filename'), "rb"),
        caption=text.get(choice).get('text')
    )

    await callback.message.delete()
