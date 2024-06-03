from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class AuthState(StatesGroup):
    waiting_phone = State()
    waiting_iin = State()


class AuthClientState(StatesGroup):
    waiting_phone = State()
    waiting_name = State()
    waiting_birthday_date = State()
    waiting_gender = State()
