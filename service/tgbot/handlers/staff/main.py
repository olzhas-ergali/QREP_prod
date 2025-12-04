from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.dispatcher.filters.state import State

from service.API.infrastructure.database.models import User
from service.tgbot.keyboards.staff.staff import main_btns
from service.tgbot.misc.delete import remove
from sqlalchemy.orm import selectinload
from sqlalchemy import select


async def start_handler(
        message: Message,
        user: User,
        state: FSMContext
):
    _ = message.bot.get("i18n")
    await state.finish()
    await remove(message, 1)
    await remove(message, 0)

    # --- ИЗМЕНЕНИЕ: Получаем ФИО из профиля ---
    session = state.storage.data[str(message.from_user.id)][str(message.from_user.id)]['session']
    
    stmt = select(User).options(selectinload(User.profile)).where(User.id == user.id)
    full_user: User = await session.scalar(stmt)
    
    user_fullname = full_user.profile.fullname if full_user and full_user.profile else "Сотрудник"

    text = _("{name} вас приветствует команда Qazaq Republic! Желаем приятных покупок. 🤗").format(name=user_fullname)
    
    await message.answer(
        text=text,
        reply_markup=await main_btns(user, _)
    )

