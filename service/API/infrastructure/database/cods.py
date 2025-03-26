from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Text, DateTime, func, String, Boolean, select
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.models import Base


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

    @classmethod
    async def get_code(
            cls,
            code: str,
            session: AsyncSession
    ):
        stmt = select(Cods).where(code == Cods.code)
        return await session.scalar(stmt)
