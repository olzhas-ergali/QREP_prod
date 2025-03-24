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
    phone_number: typing.Optional[str] = Body(
        default=None,
        alias="phone",
        description="Телефонный номер пользователя",
        example="77018192236"
    ),
    clientFullName: typing.Optional[str] = Body(
        default=None,
        alias="clientFullName",
        description="Имя клиента",
        example="Талтынбек"
    ),
    birthDate: typing.Optional[datetime.datetime] = Body(
        alias="birthDate",
        description="Дата рождение",
        example="1996-09-20T00:00:00"
    ),
    gender: typing.Optional[str] = Body(
        alias="gender",
        description="Пол",
        example="F или M"
    ),
    email: typing.Optional[str] = Body(
        alias="email",
        description="Почта",
        example="nika@example.com"
    ),
    source: typing.Optional[str] = Body(
        alias="source",
        description="Источник",
        example="Site"
    )


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
