from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from service.tgbot.keyboards.query_cb import GenderCallback
from service.tgbot.keyboards import generate
from service.tgbot.keyboards.query_cb import ChoiceCallback


async def main_btns():
    markup = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )
    btns = ['Мои бонусы',
            'Мой QR']
    for btn in btns:
        markup.add(btn)

    return markup


async def get_genders_ikb():
    markup = InlineKeyboardMarkup(1)

    man = InlineKeyboardButton(text="Муж",
                               callback_data=GenderCallback.new(gender='M',
                                                                action='gender'))

    women = InlineKeyboardButton(text="Жен",
                                 callback_data=GenderCallback.new(gender='F',
                                                                  action='gender'))

    markup.add(man)
    markup.add(women)
    return markup


async def period_btns():
    markup = InlineKeyboardMarkup()
    btns = {
        "За весь период": ChoiceCallback.new(
            choice="by_all",
            action="client_purchases"
        ),
        "За текущий месяц": ChoiceCallback.new(
            choice="by_month",
            action="client_purchases"
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