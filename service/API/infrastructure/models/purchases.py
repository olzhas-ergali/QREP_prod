import datetime
import typing
import uuid
from pydantic import BaseModel


class ModelPurchase(BaseModel):
    purchaseId: typing.Optional[str] = None
    phone: typing.Optional[str] = None
    telegramId: typing.Optional[int] = None
    createDate: typing.Optional[datetime.datetime] = datetime.datetime.now()
    products: typing.Optional[typing.List[dict]] = None
    source: typing.Optional[str] = None


class ModelClientBonus(BaseModel):
    loyaltyProgram: typing.Optional[str] = None
    accruedPoints: typing.Optional[float] = None
    writeOffPoints: typing.Optional[float] = None
    documentType: typing.Optional[str] = None
    rowNumber: typing.Optional[int] = None
    activationDate: typing.Optional[datetime.datetime] = None
    expirationDate: typing.Optional[datetime.datetime] = None
    ruleId: typing.Optional[uuid.UUID] = None
    is_activate: typing.Optional[bool] = None


class ModelPurchaseClient(BaseModel):
    purchaseId: typing.Optional[str] = None
    phone: typing.Optional[str] = None
    telegramId: typing.Optional[int] = None
    createDate: typing.Optional[datetime.datetime] = datetime.datetime.now()
    products: typing.Optional[typing.List[dict]] = None
    source: typing.Optional[str] = None
    orderNumber: typing.Optional[int] = None
    number: typing.Optional[str] = None
    shiftNumber: typing.Optional[int] = None
    ticketPrintUrl: typing.Optional[str] = None
    bonus: typing.Optional[ModelClientBonus] = None


class ModelPurchaseReturn(BaseModel):
    purchaseId: typing.Optional[str] = None
    phone: typing.Optional[str] = None
    telegramId: typing.Optional[int] = None
    createDate: typing.Optional[datetime.datetime] = datetime.datetime.now()
    products: typing.Optional[typing.List[dict]] = None
    returnId: typing.Optional[str] = "-1"
    source: typing.Optional[str] = None


class ModelClientPurchaseReturn(BaseModel):
    purchaseId: typing.Optional[str] = None
    phone: typing.Optional[str] = None
    telegramId: typing.Optional[int] = None
    createDate: typing.Optional[datetime.datetime] = datetime.datetime.now()
    products: typing.Optional[typing.List[dict]] = None
    returnId: typing.Optional[str] = "-1"
    source: typing.Optional[str] = None
    orderNumber: typing.Optional[int] = None
    number: typing.Optional[str] = None
    shiftNumber: typing.Optional[int] = None
    ticketPrintUrl: typing.Optional[str] = None
    bonus: typing.Optional[ModelClientBonus] = None


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
    positionName: typing.Optional[str] = None
    positionId: typing.Optional[str] = None
    organizationName: typing.Optional[str] = None
    organizationBin: typing.Optional[str] = None
    organizationId: typing.Optional[str] = None


class ModelStaff(BaseModel):
    iin: typing.Optional[str] = None
    phone_number: typing.Optional[str] = None
