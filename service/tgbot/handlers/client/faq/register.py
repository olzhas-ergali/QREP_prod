from aiogram import types
from aiogram.dispatcher.dispatcher import Dispatcher
from service.tgbot.handlers.client import faq
from service.tgbot.keyboards import query_cb
from service.tgbot.misc.states.client import FaqState


def register_faq_function(dp: Dispatcher):
    dp.register_callback_query_handler(
        faq.main.faq_lvl_handler,
        query_cb.FaqCallback.filter(action='faq'),
        state="*"
    )

    dp.register_callback_query_handler(
        faq.mailing.mailing_handler,
        query_cb.FaqCallback.filter(action='faq_mailings'),
        state="*"
    )

    dp.register_message_handler(
        faq.operator.operator_handler,
        text='55',
        state=FaqState.waiting_operator
    )

    dp.register_callback_query_handler(
        faq.operator.send_operator_handler,
        query_cb.OperatorCallback.filter(),
        state=FaqState.waiting_time
    )

    dp.register_callback_query_handler(
        faq.operator.user_wait_answer_handler,
        query_cb.AnswerCallback.filter(action='user_answer'),
        state="*"
    )

    dp.register_callback_query_handler(
        faq.operator.user_graded_handler,
        query_cb.AnswerCallback.filter(action='user_grade'),
        state="*"
    )
