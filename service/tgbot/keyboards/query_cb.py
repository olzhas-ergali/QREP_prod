from typing import Optional, Union
from aiogram.utils.callback_data import CallbackData


ChoiceCallback = CallbackData(
    'choice', 'choice', 'action'
)

ReviewCallback = CallbackData(
    'review', 'grade', 'action'
)

CalendarCallback = CallbackData(
    'post', 'id', 'action'
)

GenderCallback = CallbackData(
    'post', 'gender', 'action'
)
