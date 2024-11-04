from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from service.tgbot.keyboards.query_cb import AuthCallback, ContinueCallback

markup = InlineKeyboardMarkup(row_width=1)

btn1 = InlineKeyboardButton(
    text="Авторизоваться как клиент",
    callback_data=AuthCallback.new(
        id='client',
        action='auth'
    )
)

btn2 = InlineKeyboardButton(
    text="Авторизоваться как сотрудник",
    callback_data=AuthCallback.new(
        id='staff',
        action='auth'
    )
)

markup.add(btn1, btn2)


def get_continue_btn():
    btn_continue = InlineKeyboardButton(
        text="Продолжить регистрацию",
        callback_data=ContinueCallback.new(
            action='continue'
        )
    )
    return InlineKeyboardMarkup().add(btn_continue)


def staff_auth_btns():
    btn_back = InlineKeyboardButton(
        text="Назад",
        callback_data="back"
    )
    btn_repeat = InlineKeyboardButton(
        text="Повторно написать ИИН",
        callback_data="repeat"
    )

    return InlineKeyboardMarkup(row_width=1).add(btn_repeat, btn_back)
