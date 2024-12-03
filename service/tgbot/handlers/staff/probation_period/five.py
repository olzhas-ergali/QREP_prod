import typing

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.misc.probation import ProbationEvents, ProbationMessageEvent
from service.tgbot.misc.states.staff import ProbationPeriodState
from service.tgbot.models.database.probation_period import ProbationPeriodAnswer


async def probation_period_five_day_handler(
        c: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        callback_data: dict
):

    question_id = int(callback_data.get('value'))

    await c.message.edit_reply_markup()

    questions = {
        1: {
            'question': "В каких числах я получу зарплату?",
            'answer': "Зарплата выплачивается обычно до 10 числа каждого месяца."
        },
        2: {
            'question': "Как получить staff-скидку?",
            'answer': "По QR телега"
        },
        3: {
            'question': "Как отправить заявку на отпуск?",
            'answer': "Нет информации"
        }
    }

    current_question = questions[question_id]

    await c.message.answer(
        text=current_question.get('answer'),



    )


    next_question = question_id + 1

    question_obj = questions.get(next_question)

    if question_obj is None:

        await c.message.answer(
            text="""
На этом все! 
Желаю тебе успехов на работе! 
Если у тебя будут вопросы - можешь обращаться к своему руководителю или к Жанель HR (@wasrdhivlogu)       
            """
        )
        await state.finish()
        return

    await c.message.answer(
        text=question_obj.get('question')
    )

    await ProbationPeriodState.five_day.set()

