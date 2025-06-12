import typing

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InputFile
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.keyboards.staff.probation_period import get_answer_question_btn, get_evaluation_btn
from service.tgbot.misc.probation import ProbationEvents, ProbationMessageEvent
from service.tgbot.misc.states.staff import ProbationPeriodState
from service.tgbot.models.database.probation_period import ProbationPeriodAnswer
from service.tgbot.data.helpers import FILES_DIRECTORY
from service.tgbot.models.database.users import User


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
        callback_data: dict,
        user: User
):
    _ = c.bot.get('i18n')
    question_id = int(callback_data.get('value'))
    action = callback_data.get('action')
    current_day = int(callback_data.get('current_day'))
    await c.message.edit_reply_markup()

    questions = {
        1: {
            'answer': _('Отлично!Записала тебя онлайн на наш welcome training. Welcome training проходит в первые дни каждого месяца. Более подробную информацию тебе даст твой руководитель :)\n\nЕсли у тебя остались какие- то вопросы - прошу написать HR менеджеру.'),
            'files': {
                'kaz': FILES_DIRECTORY / "HR Байланыс нөмірі.pdf",
                'rus': FILES_DIRECTORY / "контакты HR.pdf"
            }
        },
        2: {
            'answer': _('Отлично! Передала информацию руководителю, Welcome training проходит в первые дни каждого месяца. Ждем тебя обязательно в офисе.')
        }
    }
    current_days = {
        True: {
            'answer': _('Рад, что онбординг помог тебе! Если появятся вопросы — всегда можешь обратиться ко мне или HR-команде. Добро пожаловать в QR Family!')
        },
        False: {
            'answer': _('Спасибо за твой отзыв! Нам важно, чтобы процесс адаптации был максимально комфортным. HR-менеджер свяжется с тобой, чтобы узнать, что можно улучшить.')
        }
    }

    if action == 'five_day':
        await ProbationPeriodAnswer(
            user_id=c.from_user.id,
            day=current_day,
            question="Перед тем как мы закончим, оцени, насколько онбординг был полезным для тебя:",
            answer=str(question_id)
        ).save(session)
        current_question = current_days[True if question_id > 3 else False]
        await state.finish()
        return await c.message.answer(
            text=current_question.get('answer')
        )
    current_question = questions[question_id]
    if current_question.get('files'):
        await ProbationPeriodAnswer(
            user_id=c.from_user.id,
            day=current_day,
            question="Как тебе будет удобнее пройти его?",
            answer="Онлайн" if question_id == 1 else "Оффлайн"
        ).save(session)
        await c.message.answer_document(
            caption=current_question.get('answer'),
            document=InputFile(current_question.get('files').get(user.local),
                               current_question.get('files').get(user.local).name)
        )

    else:
        await c.message.answer(
            text=current_question.get('answer')
        )
    return await c.message.answer(
        text=_(
            'Поздравляю! Ты успешно завершил онбординг. Надеюсь, это было полезно и помогло тебе лучше адаптироваться в компании.'
            '\nПеред тем как мы закончим, оцени, насколько онбординг был полезным для тебя:'),
        reply_markup=get_evaluation_btn(
            current_day=5,
            action="five_day"
        )
    )


