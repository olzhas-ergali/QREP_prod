import os

from aiogram.types.message import Message, ContentTypes
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.dispatcher.filters.state import State

from service.tgbot.keyboards.admin import admin
from service.API.infrastructure.database.models import UserTemp
from service.API.infrastructure.database.models import User
from service.tgbot.misc.delete import remove
from service.tgbot.misc.states.admin import AdminState
from service.tgbot.misc.parse import parse_phone


async def staff_phone_handler(
        message: Message,
        state: FSMContext
):
    await state.finish()
    await remove(message, 0)
    await message.answer(
        text="Напишите номер телефона сотрудника",
        reply_markup=await admin.admin_main_btns()
    )
    await AdminState.waiting_phone.set()


async def remove_handler(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    phone_number = parse_phone(message.text)
    await remove(message, 0)

    stmt = select(User).options(joinedload(User.profile)).where(User.phone_number == phone_number)
    user: User | None = await session.scalar(stmt)

    if not user or not user.profile:
        text = "Такого сотрудника нету базе"
    else:
        text = "Вы убрали сотрудника"
        user.profile.is_active = False
        user.profile.date_dismissal = datetime.datetime.now() # Рекомендуется также ставить дату увольнения
        session.add(user.profile)
        await session.commit()

    await message.answer(
        text=text,
        reply_markup=await admin.choice_btns()
    )
    await state.finish()
