from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.dispatcher.filters.state import State

from service.tgbot.models.database.users import User
from service.tgbot.keyboards.staff.staff import main_btns
from service.tgbot.misc.delete import remove


async def start_handler(
        message: Message,
        user: User,
        state: FSMContext
):
    _ = message.bot.get("i18n")
    await state.finish()
    await remove(message, 1)
    await remove(message, 0)
    #text = "Добро пожаловать в дружную команду Qazaq Republic, " + staff.name + "🤗"
    text = _("{name} вас приветствует команда Qazaq Republic! Желаем приятных покупок. 🤗").format(name=user.name)
    await message.answer(
        text=text,
        reply_markup=await main_btns(user, _)
    )

