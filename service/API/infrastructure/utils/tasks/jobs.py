import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from service.API.infrastructure.database.notification import MessageLog, MessageTemplate, EventType
from service.API.infrastructure.database.models import Client, ClientPurchase, ClientPurchaseReturn
from service.API.infrastructure.database.loyalty import ClientBonusPoints
from service.tgbot.lib.SendPlusAPI.send_plus import SendPlus
from service.API.config import settings
from service.API.infrastructure.utils.smpt import Mail


async def bonus_credit_notification(
        db_session
):
    session: AsyncSession = db_session()

    wb = SendPlus(
        client_id=settings.wb_cred.client_id,
        client_secret=settings.wb_cred.client_secret,
        waba_bot_id=settings.wb_cred.wb_bot_id
    )

    client_bonuses = await ClientBonusPoints.get_credited_bonuses(
        session=session,
        data=datetime.datetime.now().date()
    )
    clients_credits = {}
    for r in client_bonuses:
        if not clients_credits.get(r.client_purchases_id):
            clients_credits[r.client_purchases_id] = {
                "client_id": r.client_id,
                "purchase_id": r.client_purchases_id,
                "accrued_points": r.accrued_points,
                "write_off_points": r.write_off_points,
                "expiration_date": r.expiration_date,
                "activation_date": r.activation_date
            }
            logging.info(r.client_purchases_id)
            res = await ClientBonusPoints.get_by_purchase_id(
                session=session,
                purchase_id=r.client_purchases_id,
                accrued_points=r.accrued_points
            )
            logging.info(len(res))
            if len(res) > 0:
                clients_credits.pop(r.client_purchases_id)

    mail = Mail()
    for key, value in clients_credits.items():
        client = await Client.get_client_by_id(
            session=session,
            client_id=value.get('client_id')
        )
        purchase = await ClientPurchase.get_by_purchase_id(
            session=session,
            purchase_id=key
        )
        local = await wb.get_local_by_phone(
            phone=client.phone_number
        )
        template_mail = await MessageTemplate.get_message_template(
            session=session,
            channel="Email",
            event_type=EventType.points_credited_email,
            local=local,
            audience_type="client"
        )
        if purchase.mc_id is not None:
            event_type = EventType.points_credited_whatsapp
            template_wa = await MessageTemplate.get_message_template(
                session=session,
                channel="WhatsApp",
                event_type=EventType.points_credited_whatsapp,
                local=local,
                audience_type="client"
            )
        else:
            event_type = EventType.points_credited_whatsapp_offline
            template_wa = await MessageTemplate.get_message_template(
                session=session,
                channel="WhatsApp",
                event_type=EventType.points_credited_whatsapp_offline,
                local=local,
                audience_type="client"
            )
        await mail.send_message(
            message=template_mail.body_template.format(name=client.name, cashback=value.get("accrued_points")),
            subject=template_mail.title_template,
            to_address=client.email
        )
        log = MessageLog(
            clint_id=client.id,
            channel="Email",
            event_type=EventType.points_credited_email,
            local=local,
            status="Good",
            message_content=template_mail.body_template.format(name=client.name, cashback=value.get("accrued_points"))
        )
        session.add(log)
        await wb.send_by_phone(
            phone=client.phone_number,
            bot_id=settings.wb_cred.wb_bot_id,
            text=template_wa.title_template.format(name=client.name, cashback=value.get("accrued_points"))
        )
        log = MessageLog(
            clint_id=client.id,
            channel="WhatsApp",
            event_type=event_type,
            local=local,
            status="Good",
            message_content=template_wa.title_template.format(name=client.name, cashback=value.get("accrued_points"))
        )
        session.add(log)
        await session.commit()
    await session.close()

