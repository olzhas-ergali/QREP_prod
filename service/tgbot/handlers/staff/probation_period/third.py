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

    current_day = int(callback_data.get('current_day'))
    value = callback_data.get('value')

    text = {
        'Да': """
Круто! Теперь мы можем быть на связи всегда!
Тамаша! Енді біз әрдайым байланыста бола аламыз!
        """,
        "Нет": """
Очень жаль… Напиши, пожалуйста, Севинч (@seviiinchx), чтобы она добавила тебя в группы
Өкінішті… Севинчке (телефон нөмірі) жазып, сені топтарға қосуын сұрай аласын!
        """
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
        current_day=current_day
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
    data = await state.get_data()
    current_day = data.get('current_day')
    current_stage_id = data.get('current_stage_id', 0)
    events = [
        ProbationMessageEvent(
            text="А это на случай, если у тебя есть вопросы по работе с Bitrix24:\n\n"
                 "Бұл жағдайда егер Bitrix24 жүйесімен жұмыс істеуге қатысты сұрақтарың болса, "
                 "төмендегідей әрекет етуге болады:\n"
                 "https://bitrix.qazaqrepublic.com/~agiLB",
            is_next=True
        ),
        ProbationMessageEvent(
            text="Если у тебя остались вопросы по Bitrix, "
                 "прошу обратиться к Жулдыз (@Nurpeissova_Zhuldyz) Спасибо за внимание! До завтра :)"
                 "Егер Bitrix24 бойынша сұрақтарың болса, Жұлдызға (телефон нөмірі) жаза аласын. "
                 "Назар аударғаның үшін рахмет! Ертең кездескенше :)",
            is_next=True
        ),
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
        await ProbationPeriodState.third_day.set()

    except FinishProbationEvent:
        await state.reset_state(with_data=True)