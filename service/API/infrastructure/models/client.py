import datetime
import typing

from pydantic import BaseModel


class ModelClient(BaseModel):
    telegramId: typing.Optional[int] = None