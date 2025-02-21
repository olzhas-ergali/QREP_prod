import typing

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.data.helpers import FILES_DIRECTORY
from service.tgbot.misc.probation import ProbationEvents, ProbationMessageEvent, FinishProbationEvent, ProbationMedia
from service.tgbot.misc.states.staff import ProbationPeriodState
from service.tgbot.models.database.probation_period import ProbationPeriodAnswer


async def probation_period_third_day_handler(
        c: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        callback_data: dict
):
    _ = c.bot.get("i18n")
    current_day = int(callback_data.get('current_day'))
    value = callback_data.get('value')

    text = {
        _('Да'): _('Круто! Теперь мы можем быть на связи всегда!'),
        _("Нет"): _('Очень жаль… Напиши, пожалуйста, Севинч (+7 707 926 6305), чтобы она добавила тебя в группы')
    }

    text_by_value = text.get(value)

    await c.message.edit_reply_markup()
    await c.message.answer(
        text=text_by_value
    )

    await ProbationPeriodAnswer(
        user_id=c.from_user.id,
        day=current_day,
        question="Ты уже есть во всех каналах(Bitrix24, Whatsapp, @qr.family?)",
        answer=value
    ).save(session)

    await state.update_data(
        current_day=current_day,
        value=value
    )
    await c.message.delete()


    await probation_period_third_day_events_handler(
        q=c,
        state=state,
        session=session
    )


async def probation_period_third_day_events_handler(
        q: typing.Union[CallbackQuery, Message],
        state: FSMContext,
        session: AsyncSession
):
    _ = q.bot.get("i18n")
    data = await state.get_data()
    current_day = data.get('current_day')
    current_stage_id = data.get('current_stage_id', 0)
    value = data.get('value')
    events = []
    if value == _('Да'):
        events.append(
            ProbationMessageEvent(
                text=_("А это на случай, если у тебя есть вопросы по работе с Bitrix24:") + "\nhttps://bitrix.qazaqrepublic.com/~agiLB",
                is_next=True
            )
        )
    events.append(
        ProbationMessageEvent(
            text=_("Если у тебя остались ещё вопросы по Bitrix, прошу обратиться к Жулдыз (+7 778 166 05 65) Спасибо за внимание! До завтра :)"),
            is_next=True
        )
    )

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
        await ProbationPeriodState.third_day.set()

    except FinishProbationEvent:
        await state.reset_state(with_data=True)