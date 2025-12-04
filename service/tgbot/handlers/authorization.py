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
from service.tgbot.keyboards.auth import get_auth_btns, get_local_btns


async def first_message_handler(
        message: Message,
):
    await message.answer(
'''Сәлем! Сізді Qazaq Republic және QR+ адалдық бағдарламасы бойынша жеке көмекшіңіз қарсы алады.
Мен сізге кэшбэк пен басқа да мүмкіндіктер туралы ақпаратты жылдам әрі оңай алуға көмектесемін.

Сәлем! Вас приветствует Qazaq Republic и ваш персональный помощник по программе лояльности QR+.
Я помогу вам быстро получить информацию о кэшбеке и многом другом.'''
    )
    await message.answer(
        text="Тілді таңдаңыз:\n"
             "Выберите язык:",
        reply_markup=get_local_btns()
    )


async def welcome_message_handler(
        query: CallbackQuery,
        callback_data: dict,
        session: AsyncSession,
        user: Client
):
    user.local = callback_data.get('lang')
    await user.save(session)
    _ = query.bot.get('i18n')
    text = _('''Добро пожаловать в QazaqRepublicBot
Если вы являетесь сотрудником QR! 
Для прохождения авторизации, пожалуйста
нажмите на кнопку "Авторизоваться как сотрудник".
Если вы не являетесь сотрудником QR, 
то нажмите на кнопку "Авторизоваться как клиент"''', locale=user.local)
    btns = get_auth_btns(_, local=user.local)
    await query.message.edit_text(
        text=text,
        reply_markup=btns
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
    if isinstance(user, Client) and user.is_active:
        return await client_main.start_handler(
            message=callback.message,
            user=user,
            state=state,
            session=session
        )
    if isinstance(user, User) and user.is_active:
        return await staff_main.start_handler(
            message=callback.message,
            user=user,
            state=state
        )
    if callback_data.get('id') == 'client':
        await client_auth.auth_phone_handler(callback.message, state, reg, user, session)
    elif callback_data.get('id') == 'staff':
        await staff_auth.auth_phone_handler(callback.message, state)


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
            session=session,
            user=user
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
    elif reg.state == "AuthClientState:waiting_email":
        await client_auth.auth_email_handler(
            query=callback,
            user=user,
            session=session,
            state=state,
            callback_data=callback_data,
            reg=reg
        )
