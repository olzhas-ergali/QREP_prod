import os
import segno
import datetime

from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import Client
from service.tgbot.keyboards.client.faq import get_faq_ikb
from service.tgbot.data.faq import faq_texts


async def get_faq_handler(
        message: Message,
):
    await message.delete()

    await message.answer(
        text="Выберите раздел",
        reply_markup=await get_faq_ikb(faq_texts)
    )


async def faq_chapters_handler(
        callback: CallbackQuery,
        callback_data: dict
):
    lvl = int(callback_data.get('lvl'))
    if lvl > 1:
        await callback.message.edit_text("Выберите язык")
    if lvl > 2:
        await callback.message.edit_text(
            text=faq_texts.get(callback_data.get('chapter')),
            reply_markup=await get_faq_ikb(
                faq_lvl=faq_texts.get(callback_data.get('chapter')),
                chapter=callback_data.get('chapter'),
                btn_lvl=lvl
            )
        )

    await callback.message.edit_reply_markup(
        reply_markup=await get_faq_ikb(
            faq_lvl=faq_texts.get(callback_data.get('chapter')) if callback_data.get('chapter') else faq_texts,
            chapter=callback_data.get('chapter'),
            btn_lvl=lvl
        )
    )
