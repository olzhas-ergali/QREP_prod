import typing
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from service.API.infrastructure.database.models import User
from service.tgbot.keyboards import generate
from service.tgbot.keyboards.query_cb import ChoiceCallback, LocalCallback


def phone_number_btn(
        _
):
    markup = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )
    markup.add(
        KeyboardButton(_("Поделиться телефоном"), request_contact=True)
    )
    return markup


async def main_btns(
        user: User,
        _: typing.Callable[[str, str | None], str],
):
    markup = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )
    # + NEW (безопасное получение локали)
    user_locale = user.profile.local if user.profile else "rus"

    # - OLD
    # btns = [_('Мои покупки', locale=user.local),
    #         _('Мой QR', locale=user.local),
    #         _('Инструкция', locale=user.local),
    #         _('Сменить язык', locale=user.local)]
    # + NEW
    btns = [_('Мои покупки', locale=user_locale),
            _('Мой QR', locale=user_locale),
            _('Инструкция', locale=user_locale),
            _('Сменить язык', locale=user_locale)]
            
    for btn in btns:
        markup.add(btn)

    # - OLD
    # if user.is_admin:
    # + NEW
    if user.profile and user.profile.is_admin:
        markup.add('Админ панель')

    return markup


async def choice_staff_btns(
        _: typing.Callable[[str], str]
):
    markup = InlineKeyboardMarkup()
    btns = {
        _("За весь период"): ChoiceCallback.new(
            choice="by_all",
            action="purchases"
        ),
        _("За текущий месяц"): ChoiceCallback.new(
            choice="by_month",
            action="purchases"
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


async def instruction_staff_btns():
    markup = InlineKeyboardMarkup()
    btns = {
        "Qazaqsha 🇰🇿": ChoiceCallback.new(
            choice="kaz",
            action="instruction"
        ),
        "На русском 🇷🇺": ChoiceCallback.new(
            choice="rus",
            action="instruction"
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


async def change_locale(
        action: str = "change_local"
):
    markup = InlineKeyboardMarkup()
    btns = {
        "Qazaqsha 🇰🇿": LocalCallback.new(
            lang="kaz",
            action=action
        ),
        "Русский 🇷🇺": LocalCallback.new(
            lang="rus",
            action=action
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
