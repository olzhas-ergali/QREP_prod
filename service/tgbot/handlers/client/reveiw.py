import os
import segno
import datetime

from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import Client, ClientReview
from service.tgbot.misc.states.client import NotificationState
from service.tgbot.keyboards.client.client import main_btns
from service.tgbot.misc.delete import remove


async def review_handler(
        callback_query: CallbackQuery,
        user: Client,
        state: FSMContext,
        session: AsyncSession,
        callback_data: dict
):
    await state.finish()
    grade = int(callback_data.get('grade'))
    text = "Рахмет! Расскажите, "\
           "пожалуйста, почему поставили такую оценку? "\
           "Что нам стоит улучшить? Если обратной связи нет, просто ответьте '-'"
    grades = {
        1: 'Очень плохо',
        2: 'Плохо',
        3: 'Удовлетворительно',
        4: 'Хорошо',
        5: 'Отлично',
    }

    c = ClientReview()
    c.client_id = user.id
    c.client_review = "-"
    c.client_grade = grade
    c.client_grade_str = grades.get(grade)
    session.add(c)
    await session.commit()
    await state.update_data(review_id=c.id)
    await callback_query.message.edit_text(
        text=text,
    )
    await NotificationState.waiting_review.set()


async def get_client_review_handler(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    data = await state.get_data()

    c = await ClientReview.get_review_by_id(
        session=session,
        review_id=int(data.get('review_id'))
    )
    c.client_review = message.text
    session.add(c)
    await session.commit()
    await message.delete()
    await remove(message, 1)
    await message.answer(
        text="Принято! Все читаем и составляем список задач для улучшения. "
             "Если сообщение требует ответа, вернемся к вам с ответом в ближайшее время.",
        reply_markup=await main_btns()
    )
    await state.finish()

