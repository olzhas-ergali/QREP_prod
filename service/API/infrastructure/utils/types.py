from enum import Enum
from service.API.infrastructure.database.loyalty import ClientBonusPoints
from sqlalchemy import desc as order_desc, asc as order_asc


class Local:
    rus = "Русский"
    kaz = "Казахский"


class Sort(str, Enum):
    #activationDate = "activationDate"
    #expirationDate = "expirationDate"
    operationDate = "operationDate"
    createdAt = "createdAt"


class Order(str, Enum):
    asc = "asc"
    desc = "desc"
