import datetime
import typing

from pydantic import BaseModel


class ModelPurchase(BaseModel):
    purchaseId: typing.Optional[str] = None
    telegramId: typing.Optional[int] = None
    createDate: typing.Optional[datetime.datetime] = datetime.datetime.now()
    products: typing.Optional[typing.List[dict]] = None
    source: typing.Optional[str] = None


class ModelPurchaseReturn(BaseModel):
    purchaseId: typing.Optional[str] = None
    telegramId: typing.Optional[int] = None
    createDate: typing.Optional[datetime.datetime] = datetime.datetime.now()
    products: typing.Optional[typing.List[dict]] = None
    returnId: typing.Optional[str] = "-1"
    source: typing.Optional[str] = None


class ModelUser(BaseModel):
    telegramId: typing.Optional[int] = None
    name: typing.Optional[str] = None
    #fullname: typing.Optional[str] = None
    phone: typing.Optional[str] = None


class ModelUserTemp(BaseModel):
    userFullName: typing.Optional[str] = None
    idStaff: typing.Optional[str] = None
    phone: typing.Optional[str] = None
    iin: typing.Optional[str] = None
    updateDate: typing.Optional[datetime.datetime] = None
    author: typing.Optional[str] = None
    dateOfReceipt: typing.Optional[datetime.datetime] = None
    dateOfDismissal: typing.Optional[datetime.datetime] = None


class ModelStaff(BaseModel):
    iin: typing.Optional[str] = None
