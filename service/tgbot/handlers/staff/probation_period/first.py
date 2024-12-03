from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.probation_period import ProbationPeriodAnswer


async def probation_first_day_handler(
        m: Message,
        session: AsyncSession,
        state: FSMContext
):
    data = await state.get_data()
    current_day = data.get('current_day')
    text = """
На этом все! 
Увидимся завтра!
    """


    await m.answer(text)

    await ProbationPeriodAnswer(
        user_id=m.from_user.id,
        day=current_day,
        question="Вопрос",
        answer=m.text,
    ).save(session=session)

    await state.finish()