import datetime
import typing
import uuid
import enum

from sqlalchemy import (Column, Integer, BigInteger, ForeignKey, Text, DateTime,
                        func, String, Boolean, select, UUID, DECIMAL, desc, asc, Date, delete, Enum)
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.models import Base
from service.API.infrastructure.database.models import Client


class EventType(enum.Enum):
    qr_enrollment_offline = "qr_enrollment_offline"
    points_credited_email = "points_credited_email"
    points_debited_email = "points_debited_email"
    points_credited_whatsapp = "points_credited_whatsapp"
    points_debited_whatsapp = "points_debited_whatsapp"


class TriggerSource(enum.Enum):
    manual_event = "manual_event"
    postgres_trigger = "postgres_trigger"
    api_event = "api_event"


class MessageTemplate(Base):
    __tablename__ = 'message_template'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    channel = Column(String)
    even_type = Column(Enum(EventType))
    audience_type = Column(String)
    title_template = Column(String)
    body_template = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    local = Column(String)


class MessageConfig(Base):
    __tablename__ = 'message_config'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    even_type = Column(String)
    trigger_source = Column(Enum(TriggerSource))
    delivery_delay = Column(Integer)
    is_enabled = Column(Boolean)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class MessageLog(Base):
    __tablename__ = 'message_log'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    client_id = Column(String)
    channel = Column(Enum(TriggerSource))
    event_type = Column(Integer)
    message_content = Column(String)
    status = Column(String)
    sent_at = Column(DateTime, default=func.now())
    error_message = Column(String)
