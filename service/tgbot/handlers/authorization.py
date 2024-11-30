import datetime
import typing

from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.dispatcher.filters.state import State

from service.tgbot.models.database.users import RegTemp, Client, User
from service.tgbot.misc.delete import remove
from service.tgbot.handlers.staff import auth as staff_auth, main as staff_main
from service.tgbot.handlers.client import auth as client_auth, main as client_main
from service.tgbot.keyboards.auth import markup


async def first_message_handler(
        message: Message,
):
    await message.answer(
        text="Добро пожаловать в QazaqRepublicBot"
             "Если вы являетесь сотрудникм QR! "
             "Для прохождения авторизации, пожалуйста"
             "нажмите на кнопку 'Авторизоваться как сотрудник'."
             "Если вы не являетесь сотрудникм QR, "
             "то нажмите на кнопку 'Авторизоваться как клиент'",
        reply_markup=markup
    )


async def authorization_handler(
        callback: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        user: typing.Union[Client, User],
        reg: RegTemp,
        session: AsyncSession
):
    await callback.message.delete()
    if callback_data.get('id') == 'client' and not user.phone_number:
        return await client_auth.auth_phone_handler(callback.message, state, reg, user, session)
    elif isinstance(user, Client) or not user.iin:
        return await staff_auth.auth_phone_handler(callback.message, state)

    if isinstance(user, Client):
        await client_main.start_handler(
            message=callback.message,
            user=user,
            state=state
        )
    if isinstance(user, User):
        await staff_main.start_handler(
            message=callback.message,
            user=user,
            state=state
        )


async def continue_auth_handler(
        callback: CallbackQuery,
        callback_data: dict,
        user: Client,
        state: FSMContext,
        reg: RegTemp,
        session: AsyncSession
):
    #await state.set_state(reg.state)
    #methods = {
    #    "AuthClientState:waiting_phone": client_auth.auth_phone_handler,
    #    "AuthClientState:waiting_name": client_auth.auth_fio_handler,
    #    "AuthClientState:waiting_birthday_date": client_auth.get_years_handler,
    #    "AuthClientState:waiting_gender": client_auth.auth_gender_handler,
    #}

    if reg.state == "AuthClientState:waiting_phone":
        await client_auth.auth_phone_handler(
            message=callback.message,
            state=state,
            reg=reg,
            session=session
        )
    elif reg.state == "AuthClientState:waiting_name":
        await client_auth.auth_fio_handler(
            message=callback.message,
            user=user,
            state=state,
            reg=reg,
            session=session
        )
    elif reg.state == "AuthClientState:waiting_birthday_date":
        await client_auth.get_years_handler(
            message=callback.message,
            user=user,
            session=session,
            state=state,
            reg=reg
        )
    elif reg.state == "AuthClientState:waiting_gender":
        await client_auth.auth_gender_handler(
            query=callback,
            user=user,
            session=session,
            state=state,
            callback_data=callback_data,
            reg=reg
        )
