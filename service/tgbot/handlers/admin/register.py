from aiogram import Dispatcher, types

from service.tgbot.handlers import admin
from service.tgbot.keyboards import query_cb
from service.tgbot.misc.states.admin import AdminState


def register_admin_function(dp: Dispatcher):
    dp.register_message_handler(
        admin.add_staff.admin_main_handler,
        text='Админ панель',
        is_admin=True,
        state="*"
    )

    dp.register_message_handler(
        admin.add_staff.selecting_add_handler,
        text='Добавить сотрудника',
        is_admin=True,
        state="*"
    )

    dp.register_message_handler(
        admin.add_staff.admin_back_handler,
        text='Назад',
        is_admin=True,
        state="*"
    )

    dp.register_callback_query_handler(
        admin.add_staff.wait_admin_handler,
        query_cb.ChoiceCallback.filter(action="add_staff"),
        state=AdminState.waiting_answer
    )

    dp.register_message_handler(
        admin.add_staff.staff_phone_handler,
        state=AdminState.waiting_staff_name
    )

    dp.register_message_handler(
        admin.add_staff.auth_staff_handler,
        state=AdminState.waiting_staff_phone
    )

    dp.register_message_handler(
        admin.add_staff.auth_staff_handler,
        content_types=types.ContentType.CONTACT,
        state=AdminState.waiting_excel
    )

    dp.register_message_handler(
        admin.remove_staff.staff_phone_handler,
        text='Удалить сотрудника',
        is_admin=True,
        state="*"
    )

    dp.register_message_handler(
        admin.remove_staff.remove_handler,
        state=AdminState.waiting_phone
    )
