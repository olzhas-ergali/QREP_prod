from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.misc.states.staff import ProbationPeriodState
from service.tgbot.misc.probation import ProbationEvents, ProbationMessageEvent, ProbationMedia, FinishProbationEvent
from service.tgbot.data.helpers import FILES_DIRECTORY
from service.tgbot.models.database.users import User
from aiogram import types


async def probation_first_day_handler(
        q: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        user: User,
        callback_data: dict = None
):
    _ = q.bot.get("i18n")
    data = await state.get_data()
    current_stage_id = data.get('current_stage_id', 0)
    current_day = data.get('current_day')
    value = data.get('value')
    if isinstance(q, CallbackQuery):
        await q.message.delete()
    if callback_data:
        value = callback_data.get('value')
        current_day = int(callback_data.get('current_day'))
    history = {
        'kaz': FILES_DIRECTORY / "Компания тарихы.pdf",
        'rus': FILES_DIRECTORY / "История нашего Бренда.pdf"
    }
    contacts = {
        'kaz': FILES_DIRECTORY / "Байланыс нөмірлері.pdf",
        'rus': FILES_DIRECTORY / "Контакты.pdf"
    }
    texts = {
        _('Да'): _("Отлично! Давай я дополню твои знания более детальным объяснением."),
        _('Нет'): _('Ничего страшного! Я с радостью расскажу тебе больше о нашей истории бренда.')
    }
    events = [
        ProbationMessageEvent(
            text=texts.get(value),
            media=ProbationMedia(
                file_path=history.get(user.local),
                content_type=types.ContentType.DOCUMENT
            ),
            is_next=True
        ),
        ProbationMessageEvent(
            text=_("Надеюсь, эта информация была для тебя полезной! В первые месяцы работы ты всегда можешь обратиться к коллегам, указанным в презентации, по соответствующим вопросам. Обязательно сохрани её, чтобы не потерять!"),
            media=ProbationMedia(
                file_path=contacts.get(user.local),
                content_type=types.ContentType.DOCUMENT
            ),
            is_next=True
        ),
        ProbationMessageEvent(
            text=_("Подскажи, у тебя остались вопросы? Если да, то напиши, пожалуйста. Мы свяжемся и ответим на них :)"),
        ),
        ProbationMessageEvent(
            text=_("На этом все! Увидимся завтра!"),
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
            current_day=current_day,
            value=value
        )
        await ProbationPeriodState.first_day.set()

    except FinishProbationEvent:
        await state.finish()
    # await q.message.answer_document(
    #     caption=texts.get(value),
    #     document=
    # )
    #await q.message.edit_text()



# async def probation_first_day_handler(
#         m: Message,
#         session: AsyncSession,
#         state: FSMContext
# ):
#     _ = m.bot.get("i18n")
#     text = _("""
# На этом все!
# Увидимся завтра!\n
# Ертең көріскенше!
#     """)
#
#     await m.answer(text)
#
#     await ProbationPeriodAnswer(
#         user_id=m.from_user.id,
#         day=1,
#         question="Вопрос",
#         answer=m.text,
#     ).save(session=session)
#
#     await state.finish()