import datetime
import typing

from fastapi import Query, Body
from pydantic import BaseModel


class ModelClient(BaseModel):
    telegramId: typing.Optional[int] = None


class ModelAuth(BaseModel):
    phone: typing.Optional[str] = None
    #telegramId: typing.Optional[int] = None
    clientFullName: typing.Optional[str] = None
    qr: typing.Optional[bool] = True
    birthDate: typing.Optional[datetime.datetime] = datetime.datetime.now()
    gender: typing.Optional[str] = 'M'
#    local: typing.Optional[str] = 'rus'


class ModelAuthSite(BaseModel):
    phone_number: typing.Optional[str] = None
    clientFullName: typing.Optional[str] | None = None
    birthDate: typing.Optional[str] | None = None
    gender: typing.Optional[str] | None = None
    email: typing.Optional[str] | None = None
    source: typing.Optional[str] | None = None


class ModelReview(BaseModel):
    phone: typing.Optional[str] = None
    grade: typing.Optional[int] = None
    review: typing.Optional[str] = None


class ModelLead(BaseModel):
    phone: typing.Optional[str] = None
    waiting_time: typing.Optional[str] = None
    tag: typing.Optional[str] = None
    grade: typing.Optional[str] = None
    loc: typing.Optional[str] = None
