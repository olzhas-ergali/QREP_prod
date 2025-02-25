import typing

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.data.helpers import FILES_DIRECTORY
from service.tgbot.misc.probation import ProbationEvents, ProbationMessageEvent, ProbationMedia, FinishProbationEvent
from service.tgbot.misc.states.staff import ProbationPeriodState
from service.tgbot.models.database.probation_period import ProbationPeriodAnswer
from service.tgbot.models.database.users import User
from aiogram.types import InputFile, MediaGroup, InputMediaVideo
from service.tgbot.keyboards.staff.probation_period import get_action_btn


async def probation_period_second_day_handler(
        c: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        user: User,
        callback_data: dict
):
    """
    Cначала оценка
    """
    _ = c.bot.get("i18n")
    current_day = int(callback_data.get('current_day'))
    value = callback_data.get('value')
    videos = {
        'kaz': FILES_DIRECTORY / "DianaKaz.mp4",
        'rus': FILES_DIRECTORY / "DianaRus.mp4"
    }
    if int(value) <= 3:
        text = _("Очень жаль :( Давай HR менеджер свяжется с тобой, чтобы узнать что тебе не понравилось.")
    else:
        #
        text = _("Отлично! Рад, что твой первый день был успешным. Давай продолжим знакомство с нашей компанией!")
    await ProbationPeriodAnswer(
        user_id=c.from_user.id,
        day=current_day,
        question="Оцени свой первый день от 1 до 5",
        answer=value
    ).save(session)

    await state.update_data(
        current_day=current_day
    )

    try:
        await c.message.delete_reply_markup()
    except:
        pass
    await c.message.answer(
        text=text
    )

    await c.message.answer_video(
        video=InputFile(videos.get(user.local), videos.get(user.local).name),
        caption=_('Сегодня я расскажу тебе вкратце о правилах трудового распорядка в нашей компании, чтобы ты знал(а), как лучше организовать свой рабочий процесс. Это поможет тебе адаптироваться быстрее и комфортнее.')
    )

    await c.message.answer(
        text=_('А теперь - кое-что интересное! Ты уже знаешь, что у нас есть статус сотрудника, а значит, ты можешь пользоваться стафф скидкой на наши продукты. Знаешь, как её активировать?'),
        reply_markup=get_action_btn(
            values=[
                _("Да"), _("Нет")
            ],
            action='discount',
            current_day=2
        )
    )


async def probation_period_second_day_events_handler(
        q: typing.Union[CallbackQuery, Message],
        state: FSMContext,
        session: AsyncSession,
        user: User,
        callback_data: dict = None
):
    _ = q.bot.get("i18n")
    data = await state.get_data()
    current_day = data.get('current_day')
    current_stage_id = data.get('current_stage_id', 0)
    value = data.get('value')
    if isinstance(q, CallbackQuery):
        await q.message.delete_reply_markup()
    if callback_data:
        value = callback_data.get('value')
    qr = {
        'kaz': FILES_DIRECTORY / "QR staff жеңілдік.pdf",
        'rus': FILES_DIRECTORY / "staff скидка.pdf"
    }
    discount_info = {
        _('Нет'): ProbationMessageEvent(
            text=_('Не переживай, я с радостью помогу! Сейчас расскажу, как активировать твою стафф скидку.'),
            media=ProbationMedia(
                file_path=qr.get(user.local),
                content_type=types.ContentType.DOCUMENT
            ),
            is_next=True
        ),
        _('Да'): ProbationMessageEvent(
            text=_('Отлично! Ты уже в курсе, как активировать скидку! Если у тебя возникнут вопросы по этому процессу, не стесняйся обращаться, я всегда рядом, чтобы помочь.'),
            is_next=True
        )
    }

    events = [
        discount_info.get(value),
        ProbationMessageEvent(
            text=_('Какие вопросы у тебя остались? Не стесняйся, напиши их сюда — и я обязательно вернусь с ответами!'),
        ),
        ProbationMessageEvent(
            text=_('Я вернусь к тебе с ответом в ближайшее время. А пока на этом все! Желаю удачного дня, и до завтра!'),
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
            value=value
        )
        await ProbationPeriodState.second_day.set()

    except FinishProbationEvent:
        await state.finish()





