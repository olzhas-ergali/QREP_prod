from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from service.tgbot.models.database.users import Client
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
