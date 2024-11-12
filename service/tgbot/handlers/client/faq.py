import os
import segno
import datetime

from aiogram.types import InlineKeyboardMarkup
from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import Client
from service.tgbot.keyboards.client.faq import get_faq_btns_new, get_faq_ikb
from service.tgbot.data.faq import faq_texts_new, faq_texts


async def get_faq_handler(
        message: Message,
        state: FSMContext
):
    await message.delete()
    await state.finish()
    btns, items = await get_faq_btns_new(faq_texts_new)
    await message.answer(
        text="Выберите раздел",
        reply_markup=btns
    )
    await state.update_data(items=items)


async def get_faq_handler_test(
        message: Message,
        state: FSMContext
):
    await message.delete()

    await message.answer(
        text="Выберите раздел",
        reply_markup=await get_faq_ikb(faq_texts)
    )


async def faq_chapters_handler_test(
        callback: CallbackQuery,
        callback_data: dict
):
    lvl = int(callback_data.get('lvl'))
    if lvl > 1:
        await callback.message.edit_text("Выберите язык")
    if lvl > 2:
        return await callback.message.edit_text(
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
    #await state.update_data(items=items)


async def faq_chapters_handler(
        callback: CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    data = await state.get_data()
    chapter = callback_data.get('chapter')


    #if data.get('items'):
    #    items = data.get('items').get(q_text)
    if chapter != "back":
        q_text = callback.message.reply_markup.inline_keyboard[int(chapter)][0].text
        if q_text == "На русском":
            q_text = "rus"
        if q_text == "На казахском":
            q_text = "kaz"
        if data.get('prev_items'):
            prev_items = data.get('prev_items') + ":" + q_text
        else:
            prev_items = q_text
        data['items'] = data['items'].get(q_text)
        await state.update_data(prev_items=prev_items)
    else:
        data['items'] = faq_texts_new
        data_items = data.get('prev_items').split(":")
        for i in data_items[:len(data_items) - 1]:
            data['items'] = data['items'].get(i)
        await state.update_data(prev_items=":".join(data_items[:len(data_items) - 1]))
    btn, items = await get_faq_btns_new(curr_items=data.get('items'))
    if isinstance(btn, InlineKeyboardMarkup):
        await callback.message.edit_text(
            text="Выберите раздел",
            reply_markup=btn
        )
    else:
        await callback.message.edit_text(
            text=btn
        )
    await state.update_data(items=items)
