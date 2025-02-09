from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.dispatcher.filters.state import State

from service.tgbot.models.database.users import User
from service.tgbot.keyboards.staff.staff import phone_number_btn


async def phone_handler(
        m: Message,
        state: State,
        text: str = None
):
    _ = m.bot.get("i18n")
    if not text:
        text = _("Поделитесь номером телефона для авторизации")

    await m.answer(
        text=text,
        reply_markup=phone_number_btn(_)
    )

    await state.set()
