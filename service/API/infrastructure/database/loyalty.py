import datetime
import typing
import uuid

from sqlalchemy import (Column, Integer, BigInteger, ForeignKey, Text, DateTime,
                        func, String, Boolean, select, UUID, DECIMAL, desc, asc, Date, delete)
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.models import Base
from service.API.infrastructure.database.models import Client


class ClientBonusPoints(Base):
    __tablename__ = 'client_bonus_points'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    client_id = Column(
        BigInteger,
        ForeignKey("clients.id", onupdate='CASCADE', ondelete='CASCADE')
    )
    loyalty_program = Column(String)
    loyalty_program_id = Column(UUID(as_uuid=True))
    operation_date = Column(DateTime, default=func.now())
    source = Column(String)
    document_id = Column(UUID(as_uuid=True))
    document_type = Column(String)
    row_number = Column(BigInteger)
    accrued_points = Column(DECIMAL)
    write_off_points = Column(DECIMAL)
    created_at = Column(DateTime, default=func.now())
    update_at = Column(DateTime, default=func.now())
    activation_date: Column[datetime.datetime] = Column(DateTime,
                                                        default=None)
    expiration_date: Column[datetime.datetime] = Column(DateTime,
                                                        default=None)
    client_purchases_id = Column(
        String,
        ForeignKey("client_purchases.id", ondelete='CASCADE', onupdate='CASCADE'),
        nullable=True
    )
    client_purchases_return_id = Column(
        String,
        # ForeignKey("client_purchases_return.return_id", ondelete='CASCADE', onupdate='CASCADE'),
        nullable=True
    )
    #is_active = Column(Boolean)

    @classmethod
    async def get_by_client_id(
            cls,
            session: AsyncSession,
            client_id: int,
            sort,
            order: typing.Callable = asc,
    ) -> typing.Sequence['ClientBonusPoints']:
        stmt = select(ClientBonusPoints).where(
            (client_id == ClientBonusPoints.client_id) &
            (datetime.datetime.now().date() >= func.cast(ClientBonusPoints.activation_date, Date))
        ).order_by(order(sort))
        #ClientBonusPoints.expiration_date
        response = await session.execute(stmt)

        return response.scalars().all()

    @classmethod
    async def get_all_by_client_id(
            cls,
            session: AsyncSession,
            client_id: int
    ) -> typing.Sequence['ClientBonusPoints']:
        stmt = select(ClientBonusPoints).where(
            (client_id == ClientBonusPoints.client_id)
        ).order_by(asc(ClientBonusPoints.expiration_date))
        response = await session.execute(stmt)

        return response.scalars().all()

    @classmethod
    async def get_by_client_id_limit(
            cls,
            session: AsyncSession,
            client_id: int,
            limit: int,
            offset: int
    ) -> typing.Sequence['ClientBonusPoints']:
        stmt = select(ClientBonusPoints).where(
            (client_id == ClientBonusPoints.client_id) &
            (datetime.datetime.now().date() >= func.cast(ClientBonusPoints.activation_date, Date))
        ).order_by(asc(ClientBonusPoints.expiration_date)).limit(limit).offset(offset)
        response = await session.execute(stmt)

        return response.scalars().all()

    @classmethod
    async def delete_by_return_purchase_id(
            cls,
            session: AsyncSession,
            purchase_id: str
    ) -> None:
        stmt = delete(ClientBonusPoints).where(purchase_id == ClientBonusPoints.client_purchases_return_id)
        await session.execute(stmt)

        return None

    @classmethod
    async def get_credited_bonuses(
            cls,
            session: AsyncSession,
            data: datetime.date
    ) -> typing.Sequence['ClientBonusPoints']:
#.having(func.count() == 1)
#.group_by(ClientBonusPoints.client_purchases_id)
# & ((ClientBonusPoints.write_off_points == 0) | (ClientBonusPoints.write_off_points is None))
#         stmt = select(ClientBonusPoints).where(
#             (ClientBonusPoints.client_purchases_id.in_(
#                 select(ClientBonusPoints.client_purchases_id).where(
#                     (ClientBonusPoints.client_purchases_id is not None)
#                 )
#             )) & (data == func.cast(ClientBonusPoints.activation_date, Date)) &
#             (ClientBonusPoints.client_purchases_return_id is None)
#         ).order_by(asc(ClientBonusPoints.activation_date))
        stmt = select(ClientBonusPoints).where(
            (ClientBonusPoints.client_purchases_id is not None) &
            (ClientBonusPoints.client_purchases_return_id is None) &
            (data == func.cast(ClientBonusPoints.activation_date, Date))
        ).order_by(asc(ClientBonusPoints.activation_date))

        response = await session.execute(stmt)

        return response.scalars().all()

    @classmethod
    async def get_debited_bonuses(
            cls,
            session: AsyncSession,
            days: int
    ) -> typing.Sequence['ClientBonusPoints']:
        stmt = select(ClientBonusPoints).where(
            (ClientBonusPoints.client_purchases_id.in_(
                select(ClientBonusPoints.client_purchases_id).where(
                    ClientBonusPoints.client_purchases_id is not None
                ).group_by(ClientBonusPoints.client_purchases_id).having(func.count() == 1)
            )) & ((func.cast(ClientBonusPoints.expiration_date, Date) - datetime.datetime.now().date()) == days)
            & (ClientBonusPoints.accrued_points > 0)
        ).order_by(asc(ClientBonusPoints.expiration_date))

        response = await session.execute(stmt)

        return response.scalars().all()


class BonusExpirationNotifications(Base):
    __tablename__ = 'bonus_expiration_notifications'
    id = Column(UUID(as_uuid=True), primary_key=True)
    loyalty_program = Column(String)
    loyalty_program_id = Column(
        UUID(as_uuid=True)
    )
    notify_before_days = Column(BigInteger)
    message_template = Column(String)
    created_at = Column(DateTime, default=func.now())
    update_at = Column(DateTime, default=func.now())
