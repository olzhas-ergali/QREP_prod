import typing

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from service.tgbot.keyboards.query_cb import (
    FaqCallback,
    OperatorCallback,
    AnswerCallback)
from service.tgbot.data.faq import faq_lvls


async def get_faq_btns(
        current_lvl: str
):
    markup = InlineKeyboardMarkup()
    n = len(faq_lvls.get(current_lvl))
    for i in range(n):
        faq_lvls.get(current_lvl)[i].get('callback')
        markup.add(
            InlineKeyboardButton(
                text=faq_lvls.get(current_lvl)[i].get('text'),
                callback_data=FaqCallback.new(
                    chapter=i + 1,
                    lvl=faq_lvls.get(current_lvl)[i].get('callback'),
                    action=faq_lvls.get(current_lvl)[i].get('action', 'faq')
                )
            )
        )
    return markup


async def get_times():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        *[
            InlineKeyboardButton(
                text="Сейчас/Дәл қазір",
                callback_data=OperatorCallback.new(
                    time="0",
                    action='application'
                )
            ),
            InlineKeyboardButton(
                text="Через 30 минут/30 минуттан кейін",
                callback_data=OperatorCallback.new(
                    time="30",
                    action='application'
                )
            ),
            InlineKeyboardButton(
                text="Через 1 час/1 сағаттан кейін",
                callback_data=OperatorCallback.new(
                    time="60",
                    action='application'
                )
            ),
            InlineKeyboardButton(
                text="Через 2 час/2 сағаттан кейін",
                callback_data=OperatorCallback.new(
                    time="120",
                    action='application'
                )
            )
        ]
    )

    return markup


def get_answer():
    return InlineKeyboardMarkup().add(
        *[
            InlineKeyboardButton(
                text="Да",
                callback_data=AnswerCallback.new(
                    ans="yes",
                    action='user_answer'
                )
            ),
            InlineKeyboardButton(
                text="Подключить оператора",
                callback_data=AnswerCallback.new(
                    ans="no",
                    action='user_answer'
                )
            )
        ]
    )


def get_grade_btns():
    return InlineKeyboardMarkup(row_width=1).add(
        *[
            InlineKeyboardButton(
                text="1",
                callback_data=AnswerCallback.new(
                    ans="1",
                    action='user_grade'
                )
            ),
            InlineKeyboardButton(
                text="2",
                callback_data=AnswerCallback.new(
                    ans="2",
                    action='user_grade'
                )
            ),
            InlineKeyboardButton(
                text="3",
                callback_data=AnswerCallback.new(
                    ans="3",
                    action='user_grade'
                )
            ),
            InlineKeyboardButton(
                text="4",
                callback_data=AnswerCallback.new(
                    ans="4",
                    action='user_grade'
                )
            ),
            InlineKeyboardButton(
                text="5",
                callback_data=AnswerCallback.new(
                    ans="5",
                    action='user_grade'
                )
            )
        ]
    )


