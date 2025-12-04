import typing

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from service.tgbot.keyboards.query_cb import GenderCallback, UniversalCallback
from service.tgbot.keyboards import generate
from service.tgbot.keyboards.query_cb import ChoiceCallback


async def main_btns(
        _: typing.Callable[[str], str]
):
    markup = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )
    btns = [_('Мои бонусы'),
            _('Мой QR'),
            _('Мои покупки')]
            #'FAQ']
    for btn in btns:
        markup.add(btn)

    return markup


async def get_genders_ikb(
        _: typing.Callable[[str], str]
):
    markup = InlineKeyboardMarkup(1)

    man = InlineKeyboardButton(text=_("Муж"),
                               callback_data=GenderCallback.new(gender='M',
                                                                action='gender'))

    women = InlineKeyboardButton(text=_("Жен"),
                                 callback_data=GenderCallback.new(gender='F',
                                                                  action='gender'))

    markup.add(man)
    markup.add(women)
    return markup


async def get_universal_btn(
        text: str,
        action: str
):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(
        text=text,
        callback_data=UniversalCallback.new(
            action=action
        )
    )
    markup.add(btn)
    return markup


async def period_btns(
        _: typing.Callable[[str], str]
):
    markup = InlineKeyboardMarkup()
    btns = {
        _("За весь период"): ChoiceCallback.new(
            choice="by_all",
            action="client_purchases"
        ),
        _("За текущий месяц"): ChoiceCallback.new(
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
