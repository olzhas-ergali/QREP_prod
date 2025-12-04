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
    waiting_email = State()


class ProbationPeriodState(StatesGroup):
    first_day = State()
    second_day = State()
    third_day = State()
    fourth_day = State()
    five_day = State()
