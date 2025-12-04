from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class NotificationState(StatesGroup):
    waiting_review = State()


class FaqState(StatesGroup):
    start = State()
    waiting_time = State()
    waiting_operator = State()
