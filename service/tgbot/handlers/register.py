from aiogram import types
from aiogram.dispatcher.dispatcher import Dispatcher
from service.tgbot.handlers import staff
from service.tgbot.handlers import client
from service.tgbot.misc.states.staff import AuthState, AuthClientState


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
        client.auth.auth_client_handler,
        state=AuthClientState.waiting_name
    )
