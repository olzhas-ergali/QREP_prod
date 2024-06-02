import calendar
import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from service.tgbot.data.info import MONTHS


date_callback = CallbackData(
    'date', 'year', 'month', 'day'
)


def get_months_btn(
        year: int
):
    markup = InlineKeyboardMarkup()
    markup.add(
        *[InlineKeyboardButton(
            text=month_name,
            callback_data=date_callback.new(
                year=year,
                month=month_id,
                day='0'
            )
        ) for month_name, month_id in MONTHS.items()]
    )

    return markup
