from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from service.tgbot.keyboards.query_cb import ProbationPeriodActionCallback


def get_input_question_for_probation_period_btn(
        current_day: int
):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="Написать вопрос",
            callback_data=ProbationPeriodActionCallback.new(
                current_day=current_day,
                action='question',
                value=""
            )
        )
    )

    return markup


def get_evaluation_btn(
        current_day: int,
        action: str
):
    markup = InlineKeyboardMarkup()

    evaluations = [
        i for i in range(1, 6)
    ]

    for evaluation in evaluations:
        markup.insert(
            InlineKeyboardButton(
                text=evaluation,
                callback_data=ProbationPeriodActionCallback.new(
                    current_day=current_day,
                    action=action,
                    value=evaluation
                )
            )
        )

    return markup


def get_action_btn(
        values: list[str],
        action: str,
        current_day: int
):
    markup = InlineKeyboardMarkup()

    for value in values:
        markup.add(
            InlineKeyboardButton(
                text=value,
                callback_data=ProbationPeriodActionCallback.new(
                    current_day=current_day,
                    action=action,
                    value=value
                )
            )
        )
    return markup


def get_answer_question_btn(
        current_day: int,
        action: str,
        question_id: int
):

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="Получить ответ",
            callback_data=ProbationPeriodActionCallback.new(
                action=action,
                value=question_id,
                current_day=current_day
            )
        )
    )

    return markup