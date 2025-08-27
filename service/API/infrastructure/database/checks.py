import datetime
import typing
import uuid
import enum

from sqlalchemy import (Column, BigInteger, ForeignKey, DateTime,
                        func, String, Boolean, select, UUID, DECIMAL,
                        desc, asc, or_, and_, Enum)
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.models import Base
from service.API.infrastructure.database.models import Client


class Status(enum.Enum):
    active = "active"
    annulled = "annulled"


class PromoContests(Base):
    __tablename__ = 'promo_contests'
    promo_id = Column(BigInteger, primary_key=True, autoincrement=True)
    contest_name = Column(String)
    start_date = Column(DateTime)
    date_exception = Column(DateTime, default=None)
    end_date = Column(DateTime)
    is_active = Column(Boolean)

    @classmethod
    async def get_active_promo(
            cls,
            session: AsyncSession
    ):
        stmt = select(PromoContests).where(PromoContests.is_active.is_(True))

        return await session.scalar(stmt)


class PromoCheckParticipation(Base):
    __tablename__ = 'promo_check_participation'
    participation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    promo_id = Column(
        BigInteger,
        ForeignKey("promo_contests.promo_id", ondelete='CASCADE', onupdate='CASCADE')
    )
    participation_number = Column(String, unique=True)
    check_id = Column(
        String,
        ForeignKey("client_purchases.id", ondelete='CASCADE', onupdate='CASCADE')
    )
    client_id = Column(
        BigInteger,
        ForeignKey("clients.id", onupdate='CASCADE', ondelete='CASCADE')
    )
    purchase_date = Column(DateTime, default=func.now())
    amount_initial = Column(BigInteger)
    amount_effective = Column(BigInteger)
    status = Column(Enum(Status), default=Status.active)
    annul_reason = Column(String)
    registered_at = Column(DateTime, default=func.now())
    annulled_at = Column(DateTime, default=None)

    @classmethod
    async def get_promo_by_check_id(
            cls,
            purchase_id: str,
            client_id: int,
            session: AsyncSession
    ) -> typing.Optional['PromoCheckParticipation']:
        stmt = select(PromoCheckParticipation).where(
            and_(
                purchase_id == PromoCheckParticipation.check_id,
                client_id == PromoCheckParticipation.client_id
            )
        )
        return await session.scalar(stmt)


class WhitelistDeliveryItemIds(Base):
    __tablename__ = 'whitelist_delivery_items'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name = Column(String)

    @classmethod
    async def get_delivery_ids(
            cls,
            session: AsyncSession
    ) -> typing.List:
        stmt = select(WhitelistDeliveryItemIds)
        response = await session.execute(stmt)
        items = response.scalars()
        ids = [i.id for i in items]

        return ids
