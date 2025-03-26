from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Text, DateTime, func, String, Boolean
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.base import Base


class Cods(Base):
    __tablename__ = "cods"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    code = Column(
        String, unique=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    is_active = Column(
        Boolean, default=False
    )
