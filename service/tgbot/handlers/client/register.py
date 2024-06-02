from aiogram import types
from aiogram.dispatcher.dispatcher import Dispatcher
from service.tgbot.handlers import client
from service.tgbot.keyboards.query_cb import ReviewCallback
from service.tgbot.misc.states.client import NotificationState


def register_client_function(dp: Dispatcher):
    dp.register_message_handler(
        client.main.get_my_qr_handler,
        text='Мой QR',
        is_client_auth=True,
        state="*"
    )

    dp.register_message_handler(
        client.main.get_my_bonus_handler,
        text='Мои бонусы',
        is_client_auth=True,
        state="*"
    )

    dp.register_callback_query_handler(
        client.reveiw.review_handler,
        ReviewCallback.filter(action='review'),
        state="*"
    )

    dp.register_message_handler(
        client.reveiw.get_client_review_handler,
        state=NotificationState.waiting_review
    )
