import datetime
import typing
import uuid

from sqlalchemy import (BigInteger, Column, String, select, Date,
                        DateTime, func, Integer, ForeignKey, Boolean,
                        ARRAY, JSON, not_, desc, VARCHAR, Text, CHAR, and_, UUID, DECIMAL)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    iin = Column(String, unique=True)
    name = Column(String)
    fullname = Column(String)
    phone_number = Column(String, unique=True, default=None)
    created_at = Column(DateTime, server_default=func.now())
    author = Column(String)
    date_receipt = Column(DateTime)
    date_dismissal = Column(DateTime)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    position_name = Column(String, default=None)
    position_id = Column(String, default=None)
    organization_name = Column(String, default=None)
    organization_bin = Column(String, default=None)
    organization_id = Column(String, default=None)

    @classmethod
    async def get_by_id(
            cls,
            session: AsyncSession,
            user_id: int
    ) -> 'User':
        stmt = select(User).where(
            user_id == User.id
        )

        return await session.scalar(stmt)

    @classmethod
    async def get_by_phone(
            cls,
            session: AsyncSession,
            phone: str
    ) -> 'User':
        stmt = select(User).where(
            phone == User.phone_number
        )

        return await session.scalar(stmt)

    @classmethod
    async def get_by_iin(
            cls,
            session: AsyncSession,
            iin: str
    ) -> 'User':
        stmt = select(User).where(
            iin == User.iin
        )

        return await session.scalar(stmt)

    @classmethod
    async def get_by_position_id(
            cls,
            session: AsyncSession,
            position_id: str
    ) -> 'User':
        stmt = select(User).where(
            position_id == User.position_id
        )

        return await session.scalar(stmt)

    def get_mention(self, name=None):
        if name is None:
            name = self.name

        return f"<a href='{self.id}'>{self.name}</a>"


class UserTemp(Base):
    __tablename__ = "users_temp"
    id_staff = Column(String, primary_key=True, unique=True)
    phone_number = Column(String, default=None)
    iin = Column(String)
    name = Column(String)
    author = Column(String)
    date_receipt = Column(DateTime)
    date_dismissal = Column(DateTime, default=None)
    created_at = Column(DateTime, server_default=func.now())
    update_data = Column(DateTime)
    is_fired = Column(Boolean, default=False)
    position_name = Column(String, default=None)
    position_id = Column(String, default=None)
    organization_name = Column(String, default=None)
    organization_bin = Column(String, default=None)
    organization_id = Column(String, default=None)

    @classmethod
    async def get_user_temp(
            cls,
            session: AsyncSession,
            phone: str,
    ) -> 'UserTemp':

        stmt = select(UserTemp).where(
            (phone == UserTemp.phone_number) & not_(UserTemp.is_fired)
        ).order_by(desc(UserTemp.created_at)).limit(1)

        return await session.scalar(stmt)

    @classmethod
    async def get_user_by_iin(
            cls,
            session: AsyncSession,
            iin: str,
    ) -> 'UserTemp':
        stmt = select(UserTemp).where(
            (iin == UserTemp.iin) & not_(UserTemp.is_fired)
        ).order_by(desc(UserTemp.created_at)).limit(1)

        return await session.scalar(stmt)


class PositionDiscounts(Base):
    __tablename__ = "position_discounts"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    position_id: Column[str] = Column(
        String
    )
    position_name: Column[str] = Column(
        String
    )
    discount_percentage = Column(DECIMAL)
    created_at = Column(DateTime, server_default=func.now())
    update_data = Column(DateTime, default=None)
    is_active = Column(Boolean, default=True)
    description = Column(String, default=None)
    start_date = Column(DateTime, default=None)
    end_date = Column(DateTime, default=None)
    monthly_limit = Column(BigInteger)


class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(String, primary_key=True)
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'),
    )
    products = Column(ARRAY(JSON))
    source = Column(String)
    users = relationship(
        'User',
        foreign_keys=[user_id],
        uselist=True,
        lazy='selectin'
    )


class PurchaseReturn(Base):
    __tablename__ = "purchases_return"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    purchase_id = Column(
        String,
        ForeignKey('purchases.id', ondelete='CASCADE'),
    )
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'),
    )
    products = Column(ARRAY(JSON))
    return_id = Column(String, default=None)
    source = Column(String)
    users = relationship(
        'User',
        foreign_keys=[user_id],
        uselist=True,
        lazy='selectin'
    )
    purchases = relationship(
        'Purchase',
        foreign_keys=[purchase_id],
        uselist=True,
        lazy='selectin'
    )


class Client(Base):
    __tablename__ = "clients"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    whatsapp_id = Column(VARCHAR(36))
    name = Column(String)
    fullname = Column(String)
    phone_number = Column(String, unique=True, default=None)
    gender = Column(CHAR)
    birthday_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    update_data = Column(DateTime, default=None)
    is_active = Column(Boolean, default=True)
    source = Column(String)
    activity = Column(String, default="telegram")
    local = Column(String, default="rus")

    @classmethod
    async def get_client_by_phone(
            cls,
            session: AsyncSession,
            phone: str
    ) -> 'Client':
        stmt = select(Client).where(
            phone == Client.phone_number
        )

        return await session.scalar(stmt)


class ClientPurchase(Base):
    __tablename__ = "client_purchases"
    id = Column(String, primary_key=True)
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(
        BigInteger,
        ForeignKey('clients.id', ondelete='CASCADE', onupdate='CASCADE'),
    )
    products = Column(ARRAY(JSON))
    source = Column(String)
    order_number = Column(BigInteger)
    number = Column(String)
    shift_number = Column(BigInteger)
    ticket_print_url = Column(String)
    client = relationship(
        'Client',
        foreign_keys=[user_id],
        uselist=True,
        lazy='selectin'
    )


class ClientPurchaseReturn(Base):
    __tablename__ = "client_purchases_return"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    purchase_id = Column(
        String,
        ForeignKey('client_purchases.id', ondelete='CASCADE'),
    )
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(
        BigInteger,
        ForeignKey('clients.id', ondelete='CASCADE', onupdate='CASCADE'),
    )
    products = Column(ARRAY(JSON))
    return_id = Column(String, default=None)
    source = Column(String)
    order_number = Column(BigInteger)
    number = Column(String)
    shift_number = Column(BigInteger)
    ticket_print_url = Column(String)
    client = relationship(
        'Client',
        foreign_keys=[user_id],
        uselist=True,
        lazy='selectin'
    )
    purchases = relationship(
        'ClientPurchase',
        foreign_keys=[purchase_id],
        uselist=True,
        lazy='selectin'
    )


class ClientReview(Base):
    __tablename__ = "clients_review"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    client_id = Column(
        BigInteger,
        ForeignKey('clients.id', ondelete='CASCADE', onupdate='CASCADE')
    )
    client_review = Column(
        Text
    )
    client_grade = Column(
        Integer
    )
    client_grade_str = Column(
        String
    )
    created_at = Column(DateTime, server_default=func.now())
    clients = relationship(
        'Client',
        foreign_keys=[client_id],
        uselist=True,
        lazy='selectin'
    )

    @classmethod
    async def get_review_by_id(
            cls,
            session: AsyncSession,
            review_id: int
    ) -> 'ClientReview':
        stmt = select(ClientReview).where(
            review_id == ClientReview.id
        )

        return await session.scalar(stmt)


class Revenue(Base):
    __tablename__ = 'revenue_data'
    row_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    document_id = mapped_column(UUID(as_uuid=True))
    period = mapped_column(DateTime, server_default=func.now())
    product_name = mapped_column(String)
    product_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    param_name = mapped_column(String)
    param_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    warehouse_name = mapped_column(String)
    warehouse_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    organization = mapped_column(String)
    organization_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    partner = mapped_column(String)
    phone = mapped_column(String)
    activity_type = mapped_column(String)
    manager = mapped_column(String)
    manager_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    quantity = mapped_column(Integer)
    revenue_with_vat = mapped_column(Integer)
    revenue_without_vat = mapped_column(Integer)
    currency = mapped_column(String)

    @classmethod
    async def get_revenue(
            cls,
            session: AsyncSession,
            row_id: str,
            document_id: str
    ) -> typing.Optional['Revenue']:
        stmt = select(Revenue).where(and_(Revenue.document_id == document_id, Revenue.row_id == row_id))

        return await session.scalar(stmt)

    @classmethod
    async def get_revenue_by_doc_id(
            cls,
            session: AsyncSession,
            document_id: str
    ) -> typing.Sequence['Revenue']:
        stmt = select(Revenue).where(Revenue.document_id == document_id)
        response = await session.execute(stmt)

        return response.scalars().all()


class ClientsApp(Base):
    __tablename__ = "clients_app"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    waiting_time = Column(DateTime)
    is_push = Column(Boolean, default=False)
    telegram_id = Column(
        BigInteger,
        default=None
    )
    phone_number = Column(
        String,
        default=None
    )

    @classmethod
    async def get_last_app(
            cls,
            session: AsyncSession,
            telegram_id: int
    ):
        stmt = select(ClientsApp).where((telegram_id == ClientsApp.telegram_id) & (ClientsApp.is_push != True))

        return await session.scalar(stmt)

    @classmethod
    async def get_last_app_by_phone(
            cls,
            session: AsyncSession,
            phone: str
    ):
        stmt = select(ClientsApp).where((phone == ClientsApp.phone_number) & (ClientsApp.is_push != True))

        return await session.scalar(stmt)


class ClientMailing(Base):
    __tablename__ = "clients_mailing"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    telegram_id = Column(
        BigInteger, default=None
    )
    phone = Column(
        String, default=None
    )

    @classmethod
    async def get_by_phone_number(
            cls,
            phone: str,
            session: AsyncSession
    ) -> typing.Sequence['ClientMailing']:
        stmt = select(ClientMailing).where(ClientMailing.phone == phone)

        return await session.scalar(stmt)

