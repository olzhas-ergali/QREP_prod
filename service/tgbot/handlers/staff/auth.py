import datetime
import logging
import typing

from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.dispatcher.filters.state import State

from service.tgbot.models.database.users import User, UserTemp, Client, RegTemp
from service.tgbot.handlers.auth import phone_handler
from service.tgbot.handlers.staff.main import start_handler
from service.tgbot.misc.states.staff import AuthState
from service.tgbot.misc.parse import parse_phone
from service.tgbot.misc.delete import remove
from service.tgbot.keyboards.auth import staff_auth_btns, get_auth_btns


async def auth_phone_handler(
        message: Message,
        state: FSMContext
):
    await state.finish()
    await phone_handler(message, AuthState.waiting_phone)


async def auth_iin_handler(
        message: typing.Union[Message, CallbackQuery],
        session: AsyncSession,
        user: Client,
        state: FSMContext
):
    _ = message.bot.get("i18n")
    data = await state.get_data()
    phone_number = data.get('phone')
    if not phone_number and isinstance(message, Message):
        phone_number = parse_phone(message.contact.phone_number)
        await state.update_data(phone=phone_number)
    staff = await User.get_by_phone(
        session=session,
        phone=phone_number
    )
    if staff and staff.is_active:
        staff.id = user.id
        staff.fullname = user.fullname
        await session.delete(user)
        await session.commit()
        await staff.save(session)
        return await start_handler(
            message=message,
            user=staff,
            state=state
        )
    if isinstance(message, Message):
        await message.answer(
            text=_("Введите ваш ИИН:"),
        )
    else:
        await message.message.edit_text(
            text=_("Введите ваш ИИН:"),
        )
    await AuthState.waiting_iin.set()


async def auth_staff(
        message: Message,
        session: AsyncSession,
        user: Client,
        state: FSMContext,
        reg: RegTemp
):
    _ = message.bot.get("i18n")
    data = await state.get_data()
    phone_number = data.get('phone')
    iin = message.text
    logging.info(f"authorization_staff -> {iin}")
    await remove(message, 0)
    await remove(message, 1)
    if not (user_t := await UserTemp.get_user_temp(session, iin)):
        return await message.answer(
            text=_('''
Упс, Вы у нас не работаете
Если вы еще не являетесь сотрудником, но хотели бы присоединиться к нашей команде, свяжитесь с нашим отделом кадров.
Контакты HR отдела:
Телефон: +7 (777) 777-77-77
Email: hr@qrepublic.com
'''),
            reply_markup=staff_auth_btns(_)
        )
    elif staff := await User.get_by_iin(session, iin):
        await message.answer(_("Такой ИИН уже зарегистрирован"))
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
        user_staff.position_id = user_t.position_id
        user_staff.position_name = user_t.position_name
        user_staff.organization_name = user_t.organization_name
        user_staff.organization_id = user_t.organization_id
        user_staff.organization_bin = user_t.organization_bin
        user_staff.local = user.local
        await user_staff.save(session)
        await start_handler(
            message=message,
            user=user_staff,
            state=state
        )
    if reg:
        await session.delete(reg)
    await state.finish()


async def back_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        user: Client,
        state: FSMContext
):
    _ = callback.bot.get("i18n")
    await state.finish()
    await callback.message.delete()
    btns = get_auth_btns(_, local=user.local)
    await callback.message.answer(
        text=_("Выберите способ авторизация"),
        reply_markup=btns
    )
