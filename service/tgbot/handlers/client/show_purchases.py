import os
import segno
import datetime

from aiogram.types.message import Message, ContentTypes
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import ParseMode
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import User
from service.tgbot.keyboards.client.client import period_btns
from service.tgbot.misc.delete import remove
from service.tgbot.misc.client.show_purchases import show_purchases


async def purchases_handler(
        message: Message,
        state: FSMContext
):
    await state.finish()
    await remove(message, 0)
    await message.answer(
        text="Выберите:",
        reply_markup=await period_btns()
    )


async def all_purchases_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        callback_data: dict,
        state: FSMContext
):
    _ = callback.bot.get('i18n')
    await callback.message.delete()
    texts = await show_purchases(
        session=session,
        user_id=callback.from_user.id,
        _=_
    )
    if texts:
        for text in texts:
            await callback.message.answer(
                text=text,
                parse_mode=ParseMode.HTML
            )
    else:
        await callback.message.answer(
            text=_("Вы пока не совершали покупки")
        )


async def purchases_by_date_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        callback_data: dict,
        state: FSMContext
):
    _ = callback.bot.get('i18n')
    await callback.message.delete()
    texts = await show_purchases(
        session=session,
        date=datetime.datetime.now(),
        user_id=callback.from_user.id,
        _=_
    )
    if texts:
        for text in texts:
            await callback.message.answer(
                text=text,
                parse_mode=ParseMode.HTML
            )
    else:
        await callback.message.answer(
            text=_("Вы пока не совершали покупки за этот месяц")
        )

