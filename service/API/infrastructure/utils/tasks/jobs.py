from sqlalchemy.ext.asyncio import AsyncSession
from service.API.infrastructure.database.notification import MessageLog, MessageTemplate, MessageConfig, EventType
from service.API.infrastructure.database.models import Client
from service.API.infrastructure.database.loyalty import ClientBonusPoints


async def bonus_notification(
        db_session
):
    session: AsyncSession = db_session()

    template = await MessageTemplate.get_message_template(
        session=session,
        channel="Email",
        event_type=EventType.points_debited_email,
        local="rus",
        audience_type="client"
    )



