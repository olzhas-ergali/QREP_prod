from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from service.tgbot.models.database.users import User
from service.tgbot.keyboards import generate
from service.tgbot.keyboards.query_cb import ChoiceCallback


async def admin_main_btns():
    markup = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )
    btns = ['Добавить сотрудника',
            'Удалить сотрудника',
            'Назад'
            ]
    for btn in btns:
        markup.add(btn)

    return markup


async def choice_btns():
    markup = InlineKeyboardMarkup()
    btns = {
        "Загрузка через Excel": ChoiceCallback.new(
            choice="excel",
            action="add_staff"
        ),
        "Добавить вручную": ChoiceCallback.new(
            choice="manually",
            action="add_staff"
        )
    }

    return generate.GenerateMarkupButtons(
        laylout=1,
        markup=markup,
        keyboards=[
            InlineKeyboardButton(
                text=t,
                callback_data=c
            ) for t, c in btns.items()
        ]
    ).get()
