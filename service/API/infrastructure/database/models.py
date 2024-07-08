import datetime
import typing

from sqlalchemy import (BigInteger, Column, String, select, Date,
                        DateTime, func, Integer, ForeignKey, Boolean,
                        ARRAY, JSON, not_, desc, VARCHAR, Text, CHAR)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship


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
    order_number = Column(String)
    number = Column(String)
    shift_number = Column(String)
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
    order_number = Column(String)
    number = Column(String)
    shift_number = Column(String)
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
