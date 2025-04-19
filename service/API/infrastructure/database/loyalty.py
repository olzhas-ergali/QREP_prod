from sqlalchemy import (Column, Integer, BigInteger, ForeignKey, Text, DateTime,
                        func, String, Boolean, select, UUID, DECIMAL)
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.models import Base


# class LoyaltyProgram(Base):
#     __tablename__ = 'loyalty_program'
#     id = Column(UUID(as_uuid=True), primary_key=True)
#     name = Column(String)
#     bonus_value = Column(DECIMAL)
#     currency = Column(String)
#     is_bonus_credited = Column(Boolean)
#     is_bonus_calculated = Column(Boolean)
#     max_payment_percent = Column(DECIMAL)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now())
#
#
# class LoyaltyCardTypes(Base):
#     __tablename__ = 'loyalty_card_types'
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     name = Column(String)
#     loyalty_program_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey('loyalty_program.id', ondelete='CASCADE', onupdate='CASCADE')
#     )
#     is_active = Column(Boolean)
#     valid_from = Column(DateTime, default=func.now(), nullable=False)
#     valid_to = Column(DateTime, default=func.now(), nullable=True)
#     comment = Column(String)

