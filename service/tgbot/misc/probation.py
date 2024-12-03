import typing
from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup




@dataclass
class ProbationMessageEvent:
    text: str
    reply_markup: InlineKeyboardMarkup




@dataclass
class ProbationEvents:
    events: typing.List[ProbationMessageEvent]

