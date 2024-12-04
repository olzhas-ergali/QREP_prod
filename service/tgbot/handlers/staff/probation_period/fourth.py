import typing

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.misc.probation import ProbationEvents, ProbationMessageEvent, FinishProbationEvent
from service.tgbot.misc.states.staff import ProbationPeriodState
from service.tgbot.models.database.probation_period import ProbationPeriodAnswer


async def probation_period_fourth_day_handler(
        c: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        callback_data: dict
):
    current_day = int(callback_data.get('current_day'))
    evaluation = int(callback_data.get('value'))

    if evaluation <= 3:
        text = """
Очень жаль :( Давай HR менеджер свяжется с тобой, чтобы узнать что тебе не понравилось.
        """
    else:
        text = """
отлично! Давай продолжим знакомство с компанией!
        """

    await c.message.edit_reply_markup()
    await c.message.answer(
        text=text
    )

    await ProbationPeriodAnswer(
        user_id=c.from_user.id,
        day=current_day,
        question="Насколько была  полезной информация от 1 до 5?",
        answer=str(evaluation)
    ).save(session)

    await state.update_data(
        current_day=current_day
    )

    await c.message.delete()

    await probation_period_fourth_day_events_handler(
        q=c,
        state=state,
        session=session
    )


async def probation_period_fourth_day_events_handler(
        q: typing.Union[CallbackQuery, Message],
        state: FSMContext,
        session: AsyncSession
):
    data = await state.get_data()
    current_day = data.get('current_day')
    current_stage_id = data.get('current_stage_id', 0)
    events = [
        ProbationMessageEvent(
            text="Какие есть преимущества работы в компании:",
            is_next=True
        ),
        ProbationMessageEvent(
            text="Надеюсь информация была полезной! До скорой встречи!!",
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
            active_stage_id=current_stage_id,
            current_stage_answer=q.text if isinstance(q, Message) else None
        )

        await state.update_data(
            current_stage_id=next_stage_id,
        )

        await ProbationPeriodState.fourth_day.set()
    except FinishProbationEvent:
        await state.finish()


