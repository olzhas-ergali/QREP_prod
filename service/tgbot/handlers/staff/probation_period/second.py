import typing

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.misc.probation import ProbationEvents, ProbationMessageEvent
from service.tgbot.misc.states.staff import ProbationPeriodState
from service.tgbot.models.database.probation_period import ProbationPeriodAnswer


async def probation_period_second_day_handler(
        c: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        callback_data: dict
):
    """
    Cначала оценка
    """

    current_day = int(callback_data.get('current_day'))
    value = callback_data.get('value')

    await ProbationPeriodAnswer(
        user_id=c.from_user.id,
        current_day=current_day,
        question="Оцени свой первый день от 1 до 5",
        answer=value
    ).save(session)

    await state.update_data(
        current_day=current_day
    )

    await probation_period_second_day_events_handler(
        q=c,
        state=state,
        session=session
    )
    await ProbationPeriodState.second_day.set()


async def probation_period_second_day_events_handler(
        q: typing.Union[CallbackQuery, Message],
        state: FSMContext,
        session: AsyncSession
):
    data = await state.get_data()
    current_day = data.get('current_day')
    current_stage_id = data.get('current_stage_id', 0)
    events = [
        ProbationMessageEvent(
            text="Давай я расскажу про историю появления бренда…",
            is_next=True
        ),
        ProbationMessageEvent(
            text="А что ты знаешь о Qazaq Republic?"
        ),
        ProbationMessageEvent(
            text="Очень интересно! А сейчас я покажу тебе орг.структуру)",
            is_next=True
        ),
        ProbationMessageEvent(
            text='Какие вопросы у тебя остались?'
        ),
        ProbationMessageEvent(
            text="Я вернусь к тебе с ответом в ближайшее время! А пока на этом все :) До завтра!",
            is_next=True
        )
    ]

    probation_events = ProbationEvents(
        bot=q.bot,
        user_id=q.from_user.id,
        session=session,
        events=events,
        current_day=current_day
    )


    try:
        next_stage_id = await probation_events.start(
            current_stage_id=current_stage_id,
            current_stage_answer=q.text if isinstance(q, Message) else None
        )

        await state.update_data(
            current_stage_id=next_stage_id,
        )
    except ProbationMessageEvent:
        await state.finish()





