import datetime

from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import Client
from service.tgbot.handlers.auth import phone_handler
from service.tgbot.handlers.client.main import start_handler
from service.tgbot.misc.states.staff import AuthClientState
from service.tgbot.misc.parse import parse_phone
from service.tgbot.misc.delete import remove
from service.tgbot.modules.OneС.Function_1C import authorization
from service.tgbot.keyboards.client.calendar import make_ikb_calendar, make_year_ikb
from service.tgbot.keyboards.client.client import get_genders_ikb


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
    if client := await Client.get_client_by_phone(
        session=session,
        phone=phone_number
    ):
        if client.id != user.id:
            user.gender = client.gender
            user.name = client.name
            user.birthday_date = client.birthday_date
            await session.delete(client)
            await session.commit()

            user.phone_number = phone_number
            await user.save(session)
            await start_handler(
                message=message,
                user=user,
                state=state
            )
        else:
            if user.phone_number != phone_number:
                user.phone_number = phone_number
                user.update_data = datetime.datetime.now()
                await user.save(session=session)

            #await authorization(user=user, bot=message.bot)
            await start_handler(
                message=message,
                user=user,
                state=state
            )
    elif not user.phone_number:
        await state.update_data(phone=phone_number)
        await remove(message, 1)
        await message.answer(
            "Введите ваше ФИО"
        )
        await AuthClientState.waiting_name.set()


async def get_years_handler(
        message: Message,
        user: Client,
        session: AsyncSession,
        state: FSMContext
):
    await remove(message, 1)
    await message.delete()
    await state.update_data(name=message.text)
    year = datetime.datetime.now().year
    await message.answer(
        text="Выберите год вашего рождения",
        reply_markup=await make_year_ikb(year)
    )
    await AuthClientState.waiting_birthday_date.set()


async def auth_get_other_year_handler(
        query: CallbackQuery,
        user: Client,
        session: AsyncSession,
        state: FSMContext,
        callback_data: dict
):
    year = int(callback_data.get('id').split(',')[1])
    kb = await make_year_ikb(year)
    await query.message.edit_reply_markup(reply_markup=kb)


async def auth_birthday_date_handler(
        query: CallbackQuery,
        user: Client,
        session: AsyncSession,
        state: FSMContext,
        callback_data: dict
):
    year = int(callback_data.get('id'))
    month = datetime.datetime.now().month
    await query.message.edit_text(
        text="Выберите вашу дату рождения",
        reply_markup=await make_ikb_calendar(
            month_num=month - 1,
            year_num=year
        )
    )


async def auth_get_other_month_handler(
        query: CallbackQuery,
        user: Client,
        session: AsyncSession,
        callback_data: dict
):
    month = int(callback_data.get('id').split(',')[1])
    year = int(callback_data.get('id').split(',')[2])
    if not month:
        year -= 1
        month = 12
    kb = await make_ikb_calendar(
        month_num=month,
        year_num=year
    )
    await query.message.edit_reply_markup(reply_markup=kb)


async def auth_gender_handler(
        query: CallbackQuery,
        user: Client,
        session: AsyncSession,
        state: FSMContext,
        callback_data: dict
):
    birthday = callback_data.get('id').replace('date,', "")
    await state.update_data(birthday=birthday.replace(",", "."))
    await query.message.edit_text(
        text="Выберите ваш пол",
        reply_markup=await get_genders_ikb()
    )
    await AuthClientState.waiting_gender.set()


async def auth_client_handler(
        query: CallbackQuery,
        user: Client,
        state: FSMContext,
        session: AsyncSession,
        callback_data: dict
):
    data = await state.get_data()
    await query.message.delete()
    user.phone_number = data.get('phone')
    user.name = data.get('name')
    user.gender = callback_data.get('gender')
    user.birthday_date = datetime.datetime.strptime(data.get('birthday'), "%d.%m.%Y")
    user.is_active = True
    await user.save(session=session)

    #await authorization(user=user, bot=query.message.bot)
    await start_handler(
        message=query.message,
        user=user,
        state=state
    )
