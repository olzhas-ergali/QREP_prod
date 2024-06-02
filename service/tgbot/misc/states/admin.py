from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminState(StatesGroup):
    waiting_answer = State()
    waiting_excel = State()
    waiting_staff_name = State()
    waiting_staff_phone = State()
    waiting_phone = State()
