import datetime
import typing
import uuid
from pydantic import BaseModel, Field


class ModelPurchase(BaseModel):
    purchaseId: typing.Optional[str] = None
    phone: typing.Optional[str] = None
    telegramId: typing.Optional[int] = None
    createDate: typing.Optional[datetime.datetime] = datetime.datetime.now()
    products: typing.Optional[typing.List[dict]] = None
    source: typing.Optional[str] = None


class ModelPurchaseReturn(BaseModel):
    purchaseId: typing.Optional[str] = None
    phone: typing.Optional[str] = None
    telegramId: typing.Optional[int] = None
    createDate: typing.Optional[datetime.datetime] = datetime.datetime.now()
    products: typing.Optional[typing.List[dict]] = None
    returnId: typing.Optional[str] = "-1"
    source: typing.Optional[str] = None


class ModelClientBonus(BaseModel):
    rule: typing.Optional[str] = None
    accruedPoints: typing.Optional[float] = None
    writeOffPoints: typing.Optional[float] = None
    rowNumber: typing.Optional[int] = None
    activationDate: typing.Optional[datetime.datetime] = None
    expirationDate: typing.Optional[datetime.datetime] = None
    ruleId: typing.Optional[uuid.UUID] = None
    is_activate: typing.Optional[bool] = None


class ModelProducts(BaseModel):
    paramId: typing.Optional[str] = None
    id: typing.Optional[str] = None
    name: typing.Optional[str] = None
    count: typing.Optional[int] = None
    price: typing.Optional[int] = None
    discountPrice: typing.Optional[int] = None
    discount: typing.Optional[bool] = False,
    discountPercent: typing.Optional[int] = None
    bonusesUsed: typing.Optional[int] = None
    bonusesAccrued: typing.Optional[str] = None


class ModelPurchaseClient(BaseModel):
    purchaseId: typing.Optional[str] = None
    documentType: typing.Optional[str] = None
    sourceSystem: typing.Optional[str] = None
    phone: typing.Optional[str] = None
    telegramId: typing.Optional[int] = None
    createDate: typing.Optional[datetime.datetime] = datetime.datetime.now()
    products: typing.Optional[typing.List[dict]] = None
    source: typing.Optional[str] = None
    orderNumber: typing.Optional[int] = None
    number: typing.Optional[str] = None
    shiftNumber: typing.Optional[int] = None
    ticketPrintUrl: typing.Optional[str] = None
    bonus: typing.List[ModelClientBonus] = None
    siteId: typing.Optional[str] = None
    msId: typing.Optional[str] = None


class ModelClientPurchaseReturn(BaseModel):
    purchaseId: typing.Optional[str] = None
    documentType: typing.Optional[str] = None
    sourceSystem: typing.Optional[str] = None
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
    bonus: typing.List[ModelClientBonus] = None
    siteId: typing.Optional[str] = None
    msId: typing.Optional[str] = None
    

class ModelUser(BaseModel):
    telegramId: typing.Optional[int] = None
    name: typing.Optional[str] = None
    #fullname: typing.Optional[str] = None
    phone: typing.Optional[str] = None


class ModelUserTemp(BaseModel):
    fullname: typing.Optional[str] = None
    idStaff: typing.Optional[str] = None
    updateDate: typing.Optional[datetime.datetime] = None
    author: typing.Optional[str] = None
    dateOfReceipt: typing.Optional[datetime.datetime] = None
    dateOfDismissal: typing.Optional[datetime.datetime] = None
    iin: typing.Optional[str] = None
    positionName: typing.Optional[str] = None
    positionId: typing.Optional[str] = None
    organizationName: typing.Optional[str] = None
    organizationId: typing.Optional[str] = None
    organizationBin: typing.Optional[str] = None
    organizationCity: typing.Optional[str] = None
    gender: typing.Optional[str] = None
    birthDate: typing.Optional[datetime.datetime] = None
    education: typing.Optional[str] = None
    department: typing.Optional[str] = None
    business_unit: typing.Optional[str] = Field(None, alias='businessUnit')
    work_city: typing.Optional[str] = Field(None, alias='workCity')
    phone: typing.Optional[str] = None # Это поле не из JSON, но используется в старом коде, оставляем


class ModelStaff(BaseModel):
    iin: typing.Optional[str] = None
    phone_number: typing.Optional[str] = None


class ModelClientWA(BaseModel):
    phoneNumber: typing.Optional[str] = None
    message: typing.Optional[str] = None
    email: typing.Optional[str] = None
    local: typing.Optional[str] = None
