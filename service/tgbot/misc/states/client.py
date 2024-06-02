from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class NotificationState(StatesGroup):
    waiting_review = State()
