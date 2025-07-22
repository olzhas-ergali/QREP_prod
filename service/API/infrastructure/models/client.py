import datetime
import typing

from fastapi import Query, Body
from pydantic import BaseModel
from service.API.infrastructure.database.notification import EventType

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
    phoneNumber: typing.Optional[str]
    clientFullName: typing.Optional[str] | None = None
    birthDate: typing.Optional[str] | None = None
    gender: typing.Optional[str] | None = None
    email: typing.Optional[str]
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


class ModelTemplate(BaseModel):
    channel: typing.Optional[str] = None
    event_type: typing.Optional[EventType] = None
    audience_type: typing.Optional[str] = None
    title_template: typing.Optional[str] = None
    body_template: typing.Optional[str] = None
    local: typing.Optional[str] = None

