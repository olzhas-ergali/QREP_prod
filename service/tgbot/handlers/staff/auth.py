# service/tgbot/handlers/staff/auth.py

import datetime
import logging
import typing

from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.dispatcher.filters.state import State

from service.tgbot.handlers.auth import phone_handler
from service.tgbot.handlers.staff.main import start_handler
from service.tgbot.misc.states.staff import AuthState
from service.tgbot.misc.parse import parse_phone
from service.tgbot.misc.delete import remove
from service.tgbot.keyboards.auth import staff_auth_btns, get_auth_btns
from service.API.infrastructure.database.models import User, UserTemp, Client, RegTemp, UserProfile
from sqlalchemy import select
from service.tgbot.handlers.staff.onboarding_form.main import start_onboarding_form

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
    if staff and staff.profile and staff.profile.is_active:
        # Если сотрудник уже есть и активен, но заходит как новый,
        # мы обновляем его ID на текущий Telegram ID (на случай смены аккаунта)
        # Внимание: это меняет ID пользователя в БД на новый
        
        # Удаляем старую запись, если ID отличается
        if staff.id != user.id:
             # Удаляем текущего временного юзера (middleware user)
             await session.delete(user)
             
             # Обновляем ID найденного сотрудника
             staff.id = message.from_user.id 
             staff.login_tg = message.from_user.full_name
             session.add(staff)
             await session.commit()
             
             return await start_handler(
                message=message,
                user=staff,
                state=state
             )
        else:
             # Если ID совпадает, просто логиним
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
        user: typing.Union[User, Client], # Middleware мог передать User
        state: FSMContext,
        reg: RegTemp
):
    _ = message.bot.get("i18n")
    data = await state.get_data()
    phone_number = data.get('phone')
    iin = message.text.strip()
    
    await remove(message, 0)
    await remove(message, 1)

    # Ищем профиль по ИИН
    profile_stmt = select(UserProfile).where(UserProfile.iin == iin, UserProfile.is_active == True)
    user_profile: UserProfile | None = await session.scalar(profile_stmt)

    if not user_profile:
        return await message.answer(
            text=_('''Упс, Вы у нас не работаете
Если вы еще не являетесь сотрудником, но хотели бы присоединиться к нашей команде, свяжитесь с нашим отделом кадров.
Контакты HR отдела:
Телефон: +7 (777) 777-77-77
Email: hr@qrepublic.com'''), 
            reply_markup=staff_auth_btns(_)
        )
    
    existing_user = await User.get_by_staff_id(session, user_profile.staff_id)
    if existing_user and existing_user.id != message.from_user.id:
        # Если сотрудник уже привязан к другому Telegram ID
        return await message.answer(_("Этот сотрудник уже зарегистрирован в боте под другим аккаунтом."))
    
    # ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С ID=0
    # Вместо пересоздания объекта (delete + new User), обновляем существующий
    
    # Middleware (db.py) гарантирует, что `user` это объект User с корректным telegram_id
    # Если по какой-то причине user это Client, то нужно создать User
    
    current_user_obj = user
    
    if isinstance(user, Client):
        # Если вдруг пришел Client (чего быть не должно при правильной настройке middleware для staff handlers)
        # Удаляем клиента и создаем User
        await session.delete(user)
        current_user_obj = User(id=message.from_user.id)
        session.add(current_user_obj)

    # Обновляем поля
    current_user_obj.staff_id = user_profile.staff_id
    current_user_obj.phone_number = phone_number
    current_user_obj.login_tg = message.from_user.full_name
    current_user_obj.author = "TG_BOT_REGISTRATION"
    
    # Обновляем локаль в профиле
    if hasattr(user, 'local'): # Если у старого объекта была локаль
         user_profile.local = user.local

    session.add(current_user_obj)
    session.add(user_profile)
    
    if reg:
        await session.delete(reg)
    
    await session.commit()
    await state.finish()

    await start_onboarding_form(message, state, current_user_obj)


async def back_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        user: Client,
        state: FSMContext
):
    _ = callback.bot.get("i18n")
    await state.finish()
    await callback.message.delete()
    
    local = "rus"
    if hasattr(user, 'local'):
        local = user.local
    elif hasattr(user, 'profile') and user.profile:
        local = user.profile.local
        
    btns = get_auth_btns(_, local=local)
    await callback.message.answer(
        text=_("Выберите способ авторизация"),
        reply_markup=btns
    )