import datetime
import typing
import uuid

from pydantic import BaseModel, Field


class RevenueDateModel(BaseModel):
    documentId: typing.Optional[str] = None
    period: typing.Optional[datetime.datetime] = None
    deleteStatus: typing.Optional[bool] = False
    documentType: typing.Optional[str] = None
    checks: typing.Optional[int] = None
    returns: typing.Optional[int] = None
    
    # --- Исправляем маппинг ---
    # Внутри кода используем snake_case, но принимаем ключи от 1С через alias
    count_returns: typing.Optional[int] = Field(default=0, alias="countreturns")
    
    # 1С шлет "amountWithVATreturns"
    amount_with_vat_returns: typing.Optional[float] = Field(default=0.0, alias="amountWithVATreturns")
    
    # 1С шлет "amountWithoutVATreturns" (судя по твоему логу)
    amount_without_vat_returns: typing.Optional[float] = Field(default=0.0, alias="amountWithoutVATreturns")
    
    # --- Поля по ТЗ (если они приходят в CamelCase, добавь алиасы) ---
    amountDocument: typing.Optional[float] = 0.0
    amountCard: typing.Optional[float] = 0.0
    amountCertificate: typing.Optional[float] = 0.0
    
    data: typing.List[dict] = Field(default_factory=list)

    #productName: typing.Optional[str] = None
    #productId: typing.Optional[str] = None
    #paramName: typing.Optional[str] = None
    #paramId: typing.Optional[str] = None

    # --- Раскоментил 4 поля ниже, согласно новой логике ---
    warehouseName: typing.Optional[str] = None
    warehouseId: typing.Optional[str] = None
    organization: typing.Optional[str] = None
    organizationId: typing.Optional[str] = None
    #partner: typing.Optional[str] = None
    #phone: typing.Optional[str] = None
    #activityType: typing.Optional[str] = None
    #manager: typing.Optional[str] = None
    #managerId: typing.Optional[str] = None
    #quantity: typing.Optional[int] = None
    #revenueWithVAT: typing.Optional[int] = None
    #revenueWithoutVAT: typing.Optional[int] = None
    #currency: typing.Optional[str] = None
