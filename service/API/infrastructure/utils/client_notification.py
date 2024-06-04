from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from service.API.infrastructure.database.models import Client


async def send_notification_from_client(
        bot: Bot,
        user: Client
):
    review_callback = CallbackData(
        'review', 'grade', 'action'
    )
    btns = {
        5: 'Отлично',
        4: 'Хорошо',
        3: 'Удовлетворительно',
        2: 'Плохо',
        1: 'Очень плохо',
    }
    markup = InlineKeyboardMarkup()

    for key, val in btns.items():
        btn = InlineKeyboardButton(
            text=val,
            callback_data=review_callback.new(
                grade=key,
                action='review'
            )
        )
        markup.add(btn)
    await bot.send_message(
        text="Мы ценим ваше мнение и стремимся к постоянному улучшению, "
             "просим Вас оценить качество сервиса Qazaq Republic",
        chat_id=user.id,
        reply_markup=markup
    )



