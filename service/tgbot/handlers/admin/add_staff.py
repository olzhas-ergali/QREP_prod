import os

from aiogram.types.message import Message, ContentTypes
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.dispatcher.filters.state import State

from service.tgbot.handlers.staff.main import start_handler
from service.tgbot.keyboards.admin import admin
from service.tgbot.models.database.users import UserTemp, User
from service.tgbot.misc.delete import remove
from service.tgbot.misc.states.admin import AdminState
from service.tgbot.misc.parse import parse_phone
from service.tgbot.misc.staff import StaffManager


async def admin_main_handler(
        message: Message,
        state: FSMContext
):
    await state.finish()
    await remove(message, 0)
    await message.answer(
        text="Админ панель",
        reply_markup=await admin.admin_main_btns()
    )


async def admin_back_handler(
        message: Message,
        user: User,
        state: FSMContext
):
    await state.finish()
    await start_handler(
        message=message,
        user=user,
        state=state
    )


async def selecting_add_handler(
        message: Message,
        state: FSMContext
):
    await state.finish()
    await remove(message, 0)
    text = "Выберите каким способом хотите добавить сотрудника"

    await message.answer(
        text=text,
        reply_markup=await admin.choice_btns()
    )
    await AdminState.waiting_answer.set()


async def wait_admin_handler(
        callback: CallbackQuery,
        callback_data: dict

):
    choice = callback_data.get('choice')
    if choice == 'excel':
        await callback.message.edit_text(
            text="Скиньте excel файл"
        )
        await AdminState.waiting_excel.set()
    else:
        await callback.message.edit_text(
            text="Напишите ФИО сотрудника"
        )
        await AdminState.waiting_staff_name.set()


async def staff_phone_handler(
        message: Message,
        state: FSMContext
):
    await state.update_data(name=message.text)
    await remove(message, 0)
    text = "Напишите номер телефона сотрудника в формате(77077777777)"

    await message.answer(
        text=text,
    )
    await AdminState.waiting_staff_phone.set()


async def auth_staff_handler(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):
    data = await state.get_data()
    name = data.get('name')
    phone_number = parse_phone(message.text)
    if not await session.get(UserTemp, phone_number):
        user = UserTemp(
            phone_number=phone_number,
            name=name
        )
    else:
        user = await User.get_by_phone(
            session=session,
            phone=phone_number
        )
        user.name = name
        user.is_fired = False
    session.add(user)
    await session.commit()

    await remove(message, 0)
    text = "Вы добавили сотрудника"

    await message.answer(
        text=text,
        reply_markup=await admin.admin_main_btns()
    )


async def auth_staff_excel_handler(
        message: Message,
        session: AsyncSession,
        state: FSMContext
):

    await remove(message, 0)
    if message.content_type not in ContentTypes.DOCUMENT:
        text = "Вы отправили не правильный файл, пожалуйста отправьте файл в формате excel"
        await message.answer(
            text=text,
        )

        return

    if message.document.file_name[-5::1] != '.xlsx'\
            or message.document.file_name[-4::1] != '.xls':

        await message.answer(
            text="Вы отправили не правильный файл, пожалуйста отправьте файл в формате excel"
        )
        return
    file = await message.bot.get_file(message.document.file_id)
    file_path = file.file_path
    await message.bot.download_file(file_path, "staffs.xlsx")
    print(file_path)
    await StaffManager.add_staff("staffs.xlsx", session)
    os.remove("staffs.xlsx")
    await state.finish()

    await message.answer(
        text="Вы добавили сотрудников",
        reply_markup=await admin.admin_main_btns()
    )
