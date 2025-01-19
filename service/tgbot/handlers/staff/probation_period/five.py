import typing

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InputFile
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.keyboards.staff.probation_period import get_answer_question_btn
from service.tgbot.misc.probation import ProbationEvents, ProbationMessageEvent
from service.tgbot.misc.states.staff import ProbationPeriodState
from service.tgbot.models.database.probation_period import ProbationPeriodAnswer
from service.tgbot.data.helpers import FILES_DIRECTORY



async def probation_period_five_day_handler_old(
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
    next_question_id = question_id + 1


    await c.message.answer(
        text=current_question.get('answer')
    )
    next_question_obj = questions.get(next_question_id)


    if next_question_obj is None:

        await c.message.answer(
            text="""
На этом все! 
Желаю тебе успехов на работе! 
Если у тебя будут вопросы - можешь обращаться к своему руководителю или к Жанель HR (@wasrdhivlogu)       
            """
        )
        await state.finish()
        return

    markup = get_answer_question_btn(
        current_day=5,
        action='question',
        question_id=next_question_id
    )

    await c.message.answer(
        text=next_question_obj.get('question'),
        reply_markup=markup
    )

    await ProbationPeriodState.five_day.set()


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
            'question': "Как тебе будет удобнее пройти его?\nСаған оны қалай өткен ыңғайлырақ болады?",
            'answer': {
                'kaz': """Отлично! Welcome training проходит в первые дни каждого месяца. 
Более подробную информацию тебе даст твой руководитель :) 
Если у тебя остались какие- то вопросы - прошу написать HR менеджеру (контакты)""",
                'rus': """"Керемет!  
Welcome training әр айдың алғашқы күндерінде өтеді. Толығырақ ақпаратты сенің жетекшің береді :)  
Егер сұрақтарың болса, HR менеджеріне (контактілер) жаза аласың."
"""
            },
            'files': {
                'kaz': FILES_DIRECTORY / "контакты HR каз.pdf",
                'rus': FILES_DIRECTORY / "Контакты HR русс.pdf"
            }
        }
    }

    current_question = questions[question_id]
    next_question_id = question_id + 1

    if current_question.get('files'):
        await c.message.answer_document(
            caption=current_question.get('answer').get('kaz'),
            document=InputFile(current_question.get('files').get('kaz'),
                               current_question.get('files').get('kaz').name)
        )
        await c.message.answer_document(
            caption=current_question.get('answer').get('rus'),
            document=InputFile(current_question.get('files').get('rus'),
                               current_question.get('files').get('rus').name)
        )
    else:
        await c.message.answer(
            text=f"{current_question.get('answer').get('kaz')}\n\n{current_question.get('answer').get('rus')}"
        )
    next_question_obj = questions.get(next_question_id)

    if next_question_obj is None:
        await c.message.answer(
            text="""
На этом все! 
Желаю тебе успехов на работе! 
Если у тебя будут вопросы - можешь обращаться к своему руководителю или к Жанель HR (@wasrdhivlogu)\n  
Жұмысыңда табыс тілеймін!  
Егер сұрақтарың болса, жетекшіңе немесе HR менеджеріне хабарласуға болады.
"""
        )
        await state.finish()
        return


