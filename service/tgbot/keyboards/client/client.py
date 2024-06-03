from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from service.tgbot.keyboards.query_cb import GenderCallback


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
