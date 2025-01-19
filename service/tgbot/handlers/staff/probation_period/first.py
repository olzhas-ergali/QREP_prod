from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.probation_period import ProbationPeriodAnswer


async def probation_first_day_handler(
        m: Message,
        session: AsyncSession,
        state: FSMContext
):
    text = """
На этом все! 
Увидимся завтра!\n
Ертең көріскенше!
    """

    await m.answer(text)

    await ProbationPeriodAnswer(
        user_id=m.from_user.id,
        day=1,
        question="Вопрос",
        answer=m.text,
    ).save(session=session)

    await state.finish()