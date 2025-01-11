import datetime
import typing

from pydantic import BaseModel


class PositionDiscountsModel(BaseModel):
    positionId: typing.Optional[str] = None
    positionName: typing.Optional[str] = None
    discountPercentage: typing.Optional[float] = None
    created_at: typing.Optional[datetime.datetime] = datetime.datetime.now()
    update_data: typing.Optional[datetime.datetime] = None
    is_active: typing.Optional[bool] = True
    description: typing.Optional[str] = None
    start_date: typing.Optional[datetime.datetime] = None
    end_date: typing.Optional[datetime.datetime] = None
    monthly_limit: typing.Optional[int] = None
    