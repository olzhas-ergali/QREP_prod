import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from service.API.infrastructure.database.notification import MessageLog, MessageTemplate, EventType
from service.API.infrastructure.database.models import Client, ClientPurchase, ClientPurchaseReturn
from service.API.infrastructure.database.loyalty import ClientBonusPoints
from service.API.infrastructure.utils.client_notification import send_notification_wa, send_notification_email


async def bonus_notification(
        db_session
):
    session: AsyncSession = db_session()

    client_bonuses = await ClientBonusPoints.get_credited_bonuses(
        session=session,
        data=datetime.datetime.now().date()
    )
    clients_credits = {}
    for r in client_bonuses:
        if not clients_credits.get(r.client_purchases_id):
            purchase = await ClientPurchase.get_by_purchase_id(
                session=session,
                purchase_id=r.client_purchases_id
            )
            order_number = purchase.mc_id if purchase.mc_id else purchase.ticket_print_url
            clients_credits[r.client_purchases_id] = {
                "client_id": r.client_id,
                "purchase_id": r.client_purchases_id,
                "accrued_points": r.accrued_points,
                "write_off_points": r.write_off_points,
                "expiration_date": r.expiration_date,
                "activation_date": r.activation_date,
                "formats": {
                    "cashback": r.accrued_points,
                    "order_number": order_number or "Нет"
                }
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
    for key, value in clients_credits.items():
        client = await Client.get_client_by_id(
            session=session,
            client_id=value.get('client_id')
        )
        await send_notification_wa(
            session=session,
            event_type=EventType.points_credited_whatsapp,
            client=client,
            formats=value.get("formats")
        )

    days_left = [-1, 7, 14, 30]
    clients_debits = {}
    for day in days_left:
        client_bonuses = await ClientBonusPoints.get_debited_bonuses(
            session=session,
            days=day
        )
        for r in client_bonuses:
            if not clients_debits.get(r.client_purchases_id):
                purchase = await ClientPurchase.get_by_purchase_id(
                    session=session,
                    purchase_id=r.client_purchases_id
                )
                order_number = purchase.mc_id if purchase.mc_id else purchase.ticket_print_url
                clients_debits[r.client_purchases_id] = {
                    "client_id": r.client_id,
                    "purchase_id": r.client_purchases_id,
                    "accrued_points": r.accrued_points,
                    "write_off_points": r.write_off_points,
                    "expiration_date": r.expiration_date,
                    "activation_date": r.activation_date,
                }

                if day == -1:
                    clients_debits[r.client_purchases_id]["formats"] = {
                        "cashback": r.accrued_points,
                        "client_name": "",
                        "order_number": order_number or "Нет"
                    }
                else:
                    clients_debits[r.client_purchases_id]["formats"] = {
                        "cashback": r.accrued_points,
                        "client_name": "",
                        "days_left": day
                    }
                logging.info(r.client_purchases_id)
                res = await ClientBonusPoints.get_by_purchase_id(
                    session=session,
                    purchase_id=r.client_purchases_id,
                    accrued_points=r.accrued_points
                )
                logging.info(len(res))
                if len(res) > 0:
                    clients_debits.pop(r.client_purchases_id)

    for key, value in clients_debits.items():
        client = await Client.get_client_by_id(
            session=session,
            client_id=value.get('client_id')
        )
        value.get("formats")["client_name"] = client.name
        if value.get("formats").get('days_left'):
            await send_notification_email(
                session=session,
                event_type=EventType.points_future_debit_email,
                client=client,
                formats=value.get("formats")
            )
        else:
            await send_notification_wa(
                session=session,
                event_type=EventType.points_debited_whatsapp,
                client=client,
                formats=value.get("formats")
            )
    await session.close()

