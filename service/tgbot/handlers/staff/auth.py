import datetime

from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.dispatcher.filters.state import State

from service.tgbot.models.database.users import User, UserTemp, Client
from service.tgbot.handlers.auth import phone_handler
from service.tgbot.handlers.staff.main import start_handler
from service.tgbot.misc.states.staff import AuthState
from service.tgbot.misc.parse import parse_phone
from service.tgbot.misc.delete import remove


async def auth_phone_handler(
        message: Message,
        state: FSMContext
):
    await state.finish()
    await phone_handler(message, AuthState.waiting_phone)


async def auth_iin_handler(
        message: Message,
        state: FSMContext
):
    phone_number = parse_phone(message.contact.phone_number)
    await state.update_data(phone=phone_number)
    await message.answer(
        text="Введите ваш ИИН:",
    )
    await AuthState.waiting_iin.set()


async def auth_staff(
        message: Message,
        session: AsyncSession,
        user: Client,
        state: FSMContext
):
    data = await state.get_data()
    phone_number = data.get('phone')
    iin = message.text
    await remove(message, 0)
    await remove(message, 1)
    if not (user_t := await UserTemp.get_user_temp(session, iin)):
        await message.answer("Вы не можете пройти регистрацию, "
                             "так как не являетесь сотрудником QR")
    elif await User.get_by_iin(session, iin):
        await message.answer("Такой ИИН уже зарегистрирован")
    else:
        if not (user_staff := await session.get(User, user.id)):
            user_staff = User()
            user_staff.id = user.id
            user_staff.fullname = user.fullname
            user_staff.phone_number = phone_number
        user_staff.name = user_t.name
        user_staff.date_receipt = user_t.date_receipt
        user_staff.date_dismissal = user_t.date_dismissal
        user_staff.author = user_t.author
        user_staff.is_active = True
        user_staff.iin = iin
        await user_staff.save(session)
        #await session.delete(staff)
        await start_handler(
            message=message,
            user=user,
            state=state
        )
    await state.finish()

