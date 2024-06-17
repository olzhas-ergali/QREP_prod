from sqlalchemy import (BigInteger, Column, String, select, Date,
                        DateTime, func, Integer, ForeignKey, Boolean, ARRAY, JSON)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from service.tgbot.models.database.base import Base


class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(String, primary_key=True)
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE'),
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
        ForeignKey('users.id', ondelete='CASCADE'),
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


class ClientPurchase(Base):
    __tablename__ = "client_purchases"
    id = Column(String, primary_key=True)
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE'),
    )
    products = Column(ARRAY(JSON))
    source = Column(String)
    users = relationship(
        'User',
        foreign_keys=[user_id],
        uselist=True,
        lazy='selectin'
    )


class ClientPurchaseReturn(Base):
    __tablename__ = "client_purchases_return"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    purchase_id = Column(
        String,
        ForeignKey('purchases.id', ondelete='CASCADE'),
    )
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE'),
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