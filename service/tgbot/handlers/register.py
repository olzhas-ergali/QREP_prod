from aiogram import types
from aiogram.dispatcher.dispatcher import Dispatcher
from service.tgbot.handlers import staff
from service.tgbot.handlers import client
from service.tgbot.misc.states.staff import AuthState, AuthClientState
from service.tgbot.keyboards import query_cb


def register_staff(dp: Dispatcher):
    dp.register_message_handler(
        staff.main.start_handler,
        commands=['start'],
        is_auth=True,
        state='*'
    )
    dp.register_message_handler(
        staff.auth.auth_phone_handler,
        commands=['staff'],
        #commands=['start'],
        is_auth=False,
        state="*"
    )

    dp.register_message_handler(
        staff.auth.auth_iin_handler,
        content_types=types.ContentType.CONTACT,
        is_auth=False,
        state=AuthState.waiting_phone
    )

    dp.register_message_handler(
        staff.auth.auth_staff,
        is_auth=False,
        state=AuthState.waiting_iin
    )
    register_client(dp)


def register_client(dp):
    dp.register_message_handler(
        client.auth.auth_phone_handler,
        commands=['start'],
        state="*"
    )

    dp.register_message_handler(
        client.auth.auth_fio_handler,
        content_types=types.ContentType.CONTACT,
        state=AuthClientState.waiting_phone
    )

    dp.register_message_handler(
        client.auth.get_years_handler,
        state=AuthClientState.waiting_name
    )

    dp.register_callback_query_handler(
        client.auth.auth_get_other_year_handler,
        query_cb.CalendarCallback.filter(action='year'),
        state=AuthClientState.waiting_birthday_date
    )

    dp.register_callback_query_handler(
        client.auth.auth_birthday_date_handler,
        query_cb.CalendarCallback.filter(action='birth_year'),
        state=AuthClientState.waiting_birthday_date
    )

    dp.register_callback_query_handler(
        client.auth.auth_get_other_month_handler,
        query_cb.CalendarCallback.filter(action='calendar'),
        state=AuthClientState.waiting_birthday_date
    )

    dp.register_callback_query_handler(
        client.auth.auth_gender_handler,
        query_cb.CalendarCallback.filter(action='mast'),
        state=AuthClientState.waiting_birthday_date
    )

    dp.register_callback_query_handler(
        client.auth.auth_client_handler,
        query_cb.GenderCallback.filter(action='gender'),
        state=AuthClientState.waiting_gender
    )
