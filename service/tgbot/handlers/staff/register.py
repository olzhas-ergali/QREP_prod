from aiogram.dispatcher.dispatcher import Dispatcher

from service.tgbot.handlers import staff
from service.tgbot.handlers.staff.probation_period import register_probation_period
from service.tgbot.keyboards.query_cb import ChoiceCallback


def register_staff_function(dp: Dispatcher):
    dp.register_message_handler(
        staff.show_purchases.purchases_handler,
        text='Мои покупки',
        is_auth=True,
        state="*"
    )

    dp.register_message_handler(
        staff.show_purchases.qr_handler,
        text='Мой QR',
        is_auth=True,
        state="*"
    )

    dp.register_callback_query_handler(
        staff.show_purchases.all_purchases_handler,
        ChoiceCallback.filter(action='purchases', choice='by_all'),
        is_auth=True,
        state="*"
    )

    dp.register_callback_query_handler(
        staff.show_purchases.purchases_by_date_handler,
        ChoiceCallback.filter(action='purchases', choice='by_month'),
        is_auth=True,
        state="*"
    )

    dp.register_message_handler(
        staff.show_purchases.choice_instruction_handler,
        text='Инструкция',
        is_auth=True,
        state="*"
    )

    dp.register_callback_query_handler(
        staff.show_purchases.get_instruction_handler,
        ChoiceCallback.filter(action='instruction'),
        is_auth=True,
        state="*"
    )

    # Регистрация обработчиков испытательного срока
    #staff.probation_period.register_probation_period(dp)

