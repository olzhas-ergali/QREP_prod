import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from sqlalchemy.ext.asyncio import AsyncSession
from service.API.infrastructure.database.models import Client, ClientsApp


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


async def push_client_answer_operator(
        session: AsyncSession,
        bot: Bot,
        client_app: ClientsApp,
        client: Client
):
    ans_callback = CallbackData(
        "answer", "ans", 'id', 'action'
    )
    logging.info("Уведомление для клиентов по оценке работе оператора")
    text1 = {
        "kaz": "Да"
    }
    text2 = {
        "kaz": "Иә"
    }
    markup = InlineKeyboardMarkup().add(
        *[
            InlineKeyboardButton(
                text=text1.get(client.local),
                callback_data=ans_callback.new(
                    ans="yes",
                    id=client.id,
                    action='user_answer'
                )
            ),
            InlineKeyboardButton(
                text=text2.get(client.local),
                callback_data=ans_callback.new(
                    ans="no",
                    id=client.id,
                    action='user_answer'
                )
            )
        ]
    )
    try:
        await bot.send_message(
            chat_id=client_app.telegram_id,
            text="Ваш вопрос решен",
            reply_markup=markup
        )
        client.is_push = True
        session.add(client)
    except Exception as ex:
        logging.exception(ex)

    session_bot = await bot.get_session()
    await session_bot.close()
    await session.commit()
