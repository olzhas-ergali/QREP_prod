from aiogram import types
from aiogram.dispatcher.dispatcher import Dispatcher
from service.tgbot.handlers import client
from service.tgbot.keyboards import query_cb
from service.tgbot.misc.states.client import NotificationState, FaqState


def register_client_function(dp: Dispatcher):
    register_faq_function(dp)

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

    # dp.register_message_handler(
    #     client.faq.get_faq_handler,
    #     text='FAQ',
    #     is_client_auth=True,
    #     state="*"
    # )

    dp.register_callback_query_handler(
        client.reveiw.review_handler,
        query_cb.ReviewCallback.filter(action='review'),
        state="*"
    )

    dp.register_message_handler(
        client.reveiw.get_client_review_handler,
        state=NotificationState.waiting_review
    )

    dp.register_message_handler(
        client.show_purchases.purchases_handler,
        text='Мои покупки',
        state="*"
    )

    dp.register_callback_query_handler(
        client.show_purchases.all_purchases_handler,
        query_cb.ChoiceCallback.filter(action='client_purchases', choice='by_all'),
        state="*"
    )

    dp.register_callback_query_handler(
        client.show_purchases.purchases_by_date_handler,
        query_cb.ChoiceCallback.filter(action='client_purchases', choice='by_month'),
        state="*"
    )


def register_faq_function(dp: Dispatcher):
    dp.register_callback_query_handler(
        client.faq.faq_chapters_handler,
        query_cb.FaqNewCallback.filter(action='faq'),
        state="*"
    )

    dp.register_callback_query_handler(
        client.faq.mailing_handler,
        query_cb.MailingsNewCallback.filter(),
        state="*"
    )

    dp.register_callback_query_handler(
        client.faq.mailing_handler,
        query_cb.MailingsNewCallback.filter(),
        state="*"
    )

    dp.register_message_handler(
        client.faq.operator_handler,
        text='55',
        state=FaqState.waiting_operator
    )

    dp.register_callback_query_handler(
        client.faq.send_operator_handler,
        query_cb.OperatorCallback.filter(),
        state=FaqState.waiting_time
    )

    dp.register_callback_query_handler(
        client.faq.send_operator_handler,
        query_cb.OperatorCallback.filter(),
        state=FaqState.waiting_time
    )

    dp.register_callback_query_handler(
        client.faq.user_wait_answer_handler,
        query_cb.AnswerCallback.filter(action='user_answer'),
        state="*"
    )

    dp.register_callback_query_handler(
        client.faq.user_graded_handler,
        query_cb.AnswerCallback.filter(action='user_grade'),
        state="*"
    )
