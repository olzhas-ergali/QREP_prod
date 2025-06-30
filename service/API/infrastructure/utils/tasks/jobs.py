import datetime

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
    for bonus in client_bonuses:
        purchase = await ClientPurchase.get_by_purchase_id(
            session=session,
            purchase_id=bonus.client_purchases_id
        )
        if clients_credits.get(bonus.client_id):
            clients_credits[bonus.client_id]["points"] = clients_credits[bonus.client_id]["points"] + bonus.accrued_points
        else:
            clients_credits[bonus.client_id] = {
                "points": bonus.accrued_points,
                "number": purchase.mc_id if purchase.mc_id is not None else purchase.ticket_print_url,
                "online": purchase.mc_id if True else False
            }
        # if bonus.expiration_date and bonus.expiration_date.date() == date_today and bonus.write_off_points == 0:
        #     if clients_debits.get(bonus.client_id):
        #         clients_debits[bonus.client_id]["points"] = clients_debits[bonus.client_id]["points"]
        #     else:
        #         clients_debits[bonus.client_id] = {
        #             "points": bonus.accrued_points,
        #             "online": purchase.mc_id if purchase.mc_id is not None else purchase.ticket_print_url,
        #             "days": 0
        #         }

    mail = Mail()
    for key, value in clients_credits.items():
        client = await Client.get_client_by_id(
            session=session,
            client_id=key
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
        if value.get("online"):
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
            message=template_mail.body_template.format(name=client.name, cashback=value.get("points")),
            subject=template_mail.title_template,
            to_address=["bob.ost@mail.ru"]
        )
        log = MessageLog(
            clint_id=client.id,
            channel="Email",
            event_type=EventType.points_credited_email,
            local=local,
            status="Good",
            message_content=template_mail.body_template.format(name=client.name, cashback=value.get("points"))
        )
        session.add(log)
        await wb.send_by_phone(
            phone="77075346231",
            bot_id=settings.wb_cred.wb_bot_id,
            text=template_wa.title_template.format(name=client.name, cashback=value.get("points"))
        )
        log = MessageLog(
            clint_id=client.id,
            channel="WhatsApp",
            event_type=event_type,
            local=local,
            status="Good",
            message_content=template_wa.title_template.format(name=client.name, cashback=value.get("points"))
        )
        session.add(log)
        await session.commit()
    await session.close()

