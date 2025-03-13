import datetime
import typing
import uuid

from pydantic import BaseModel


class RevenueDateModel(BaseModel):
    documentId: typing.Optional[str] = None
    period: typing.Optional[datetime.datetime] = None
    deleteStatus: typing.Optional[bool] = False
    data: typing.List[dict] = None
    #productName: typing.Optional[str] = None
    #productId: typing.Optional[str] = None
    #paramName: typing.Optional[str] = None
    #paramId: typing.Optional[str] = None
    #warehouseName: typing.Optional[str] = None
    #warehouseId: typing.Optional[str] = None
    #organization: typing.Optional[str] = None
    #organizationId: typing.Optional[str] = None
    #partner: typing.Optional[str] = None
    #phone: typing.Optional[str] = None
    #activityType: typing.Optional[str] = None
    #manager: typing.Optional[str] = None
    #managerId: typing.Optional[str] = None
    #quantity: typing.Optional[int] = None
    #revenueWithVAT: typing.Optional[int] = None
    #revenueWithoutVAT: typing.Optional[int] = None
    #currency: typing.Optional[str] = None
