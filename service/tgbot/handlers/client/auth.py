import datetime

from aiogram.types.message import Message, ContentType
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import Client
from service.tgbot.handlers.auth import phone_handler
from service.tgbot.handlers.client.main import start_handler
from service.tgbot.misc.states.staff import AuthClientState
from service.tgbot.misc.parse import parse_phone
from service.tgbot.misc.delete import remove
from service.tgbot.modules.OneС.Function_1C import authorization


async def auth_phone_handler(
        message: Message,
        state: FSMContext
):
    await state.finish()
    await phone_handler(message, AuthClientState.waiting_phone)


async def auth_fio_handler(
        message: Message,
        user: Client,
        session: AsyncSession,
        state: FSMContext
):
    await message.delete()
    phone_number = parse_phone(message.contact.phone_number)
    if not user.phone_number:
        await state.update_data(phone=phone_number)
        await remove(message, 1)
        await message.answer(
            "Введите ваше ФИО"
        )
        await AuthClientState.waiting_name.set()
    else:
        if user.phone_number != phone_number:
            user.phone_number = phone_number
            user.update_data = datetime.datetime.now()
            await user.save(session=session)

        await authorization(user=user, bot=message.bot)
        await start_handler(
            message=message,
            user=user,
            state=state
        )


async def auth_client_handler(
        message: Message,
        user: Client,
        state: FSMContext,
        session: AsyncSession
):
    data = await state.get_data()
    await remove(message, 1)
    await message.delete()
    user.phone_number = data.get('phone')
    user.name = message.text
    user.is_active = True
    await user.save(session=session)

    await authorization(user=user, bot=message.bot)
    await start_handler(
        message=message,
        user=user,
        state=state
    )
