from aiogram import Dispatcher

from service.tgbot.handlers.staff.probation_period.first import probation_first_day_handler
from service.tgbot.handlers.staff.probation_period.five import probation_period_five_day_handler
from service.tgbot.handlers.staff.probation_period.fourth import probation_period_fourth_day_events_handler, \
    probation_period_fourth_day_handler
from service.tgbot.handlers.staff.probation_period.second import (
    probation_period_second_day_handler,
probation_period_second_day_events_handler

)
from service.tgbot.handlers.staff.probation_period.third import probation_period_third_day_events_handler, \
    probation_period_third_day_handler
from service.tgbot.keyboards.query_cb import ProbationPeriodActionCallback
from service.tgbot.misc.states.staff import ProbationPeriodState


def register_probation_period(dp: Dispatcher):


    # Первый день испытательного срока
    dp.register_callback_query_handler(
        probation_first_day_handler,
        ProbationPeriodActionCallback.filter(
            action='first'
        ),
        state="*",
    )
    dp.register_message_handler(
        probation_first_day_handler,
        state=ProbationPeriodState.first_day,
    )


    # Второй день испытательного срока
    dp.register_callback_query_handler(
        probation_period_second_day_handler,
        ProbationPeriodActionCallback.filter(
            current_day="2",
            action='work_evaluation'
        ),
        state="*"
    )

    dp.register_callback_query_handler(
        probation_period_second_day_events_handler,
        ProbationPeriodActionCallback.filter(
            current_day="2",
            action='discount'
        ),
        state="*"
    )

    dp.register_message_handler(
        probation_period_second_day_events_handler,
        state=ProbationPeriodState.second_day
    )

    # Третий день испытательного срока
    dp.register_callback_query_handler(
        probation_period_third_day_handler,
        ProbationPeriodActionCallback.filter(
            current_day="3",
            action='social'
        ),
        state='*'
    )

    dp.register_message_handler(
        probation_period_third_day_events_handler,
        state=ProbationPeriodState.third_day
    )

    # Четвертый
    # dp.register_callback_query_handler(
    #     probation_period_fourth_day_handler,
    #     ProbationPeriodActionCallback.filter(
    #         current_day="4",
    #         action='evaluation_information'
    #     ),
    #     state="*"
    # )
    #
    # dp.register_message_handler(
    #     probation_period_fourth_day_events_handler,
    #     state=ProbationPeriodState.fourth_day
    # )

    # Пятый
    dp.register_callback_query_handler(
        probation_period_five_day_handler,
        ProbationPeriodActionCallback.filter(
            current_day="5",
            action='question'
        ),
        state='*'
    )
    dp.register_callback_query_handler(
        probation_period_five_day_handler,
        ProbationPeriodActionCallback.filter(
            current_day="5",
            action='five_day'
        ),
        state='*'
    )

