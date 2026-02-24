import logging

from aiogram import Bot
import typing
import uuid
from typing import Optional, Sequence
from datetime import datetime

from sqlalchemy import select, update, extract
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.config import settings
from service.API.infrastructure.database.models import ClientPurchase, ClientPurchaseReturn, Client
from service.API.infrastructure.database.loyalty import ClientBonusPoints
from service.API.infrastructure.database.checks import PromoCheckParticipation, Status, PromoContests, WhitelistDeliveryItemIds
from service.API.infrastructure.models.purchases import ModelClientBonus, ModelPurchaseClient, ModelClientPurchaseReturn
from service.API.infrastructure.database.notification import MessageLog, MessageTemplate, EventType
from service.API.infrastructure.utils.client_notification import (send_notification_wa, send_notification_email,
                                                                  send_template_wa, send_template_telegram, send_template_wa2)
from service.API.infrastructure.utils.generate import generate_promo_code


async def add_purchases(
        session: AsyncSession,
        # purchase_id: str,
        # user_id: int | None,
        # phone: str | None,
        # products: list | None,
        # order_number: int | None,
        # number: str | None,
        # shift_number: int | None,
        # ticket_print_url: str | None,
        purchases_model: ModelPurchaseClient | None,
        bonuses: typing.List[ModelClientBonus] | None
):
    user_id = None
    if not (client := await session.get(Client, purchases_model.telegramId)):
        client = await Client.get_client_by_phone(
            session=session,
            phone=purchases_model.phone
        )
    if client:
        user_id = client.id
    if await session.get(ClientPurchase, purchases_model.purchaseId) is not None:
        return {
            "status_code": 500,
            "message": "Чек уже записан",
            "purchaseId": purchases_model.purchaseId,
            "telegramId": user_id,
        }
    client_p = await ClientPurchase.get_by_client_id(
        session=session,
        client_id=user_id
    )

    purchases = ClientPurchase(
        id=purchases_model.purchaseId,
        source=purchases_model.source,
        source_system=purchases_model.sourceSystem,
        user_id=user_id,
        products=purchases_model.products,
        order_number=purchases_model.orderNumber,
        number=purchases_model.number,
        shift_number=purchases_model.shiftNumber,
        ticket_print_url=purchases_model.ticketPrintUrl,
        site_id=purchases_model.siteId,
        ms_id=purchases_model.msId
    )
    session.add(purchases)
    await session.commit()
    await session.refresh(purchases)  # избегаем MissingGreenlet: после commit объект expired, lazy load created_date в цикле по bonus запрещён в async
    order_number = purchases.ms_id if purchases.ms_id else purchases.ticket_print_url
    #client_bonus = None
    #send_template_wa
    activities = {
        'telegram': send_template_telegram,
        'wb': send_template_wa
    }
    promo_contests = await PromoContests.get_active_promo(session=session)
    # date_start = datetime.strptime("27.08.2025", "%d.%m.%Y").date()
    # date_end = datetime.strptime("27.09.2025", "%d.%m.%Y").date()
    if promo_contests and datetime.now().date() <= promo_contests.end_date.date() and datetime.now().date() >= promo_contests.start_date.date():
        price_sum = 0
        for p in purchases.products:
            ids = await WhitelistDeliveryItemIds.get_delivery_ids(session)
            #logging.info(p.get("id") + " " + p.get("name"))
            price_sum += p.get('sum') if p.get("id") not in ids else 0
        if price_sum >= 25000:
            promo = await generate_promo_code(
                session=session,
                purchase_id=purchases.id,
                client_id=client.id,
                price=price_sum,
                promo_id=promo_contests.promo_id
            )
            #"Вы участвуете в конкурсе Номер вашего участия: {promo_code}"
            await send_notification_email(
                session=session,
                event_type=EventType.promo_message,
                formats={
                    "promo_code": promo.participation_number,
                    "name": client.name
                },
                client=client
            )

    for bonus in bonuses:
        client_bonus = ClientBonusPoints()
        client_bonus.id = uuid.uuid4()
        client_bonus.client_id = user_id
        client_bonus.loyalty_program = bonus.rule
        client_bonus.loyalty_program_id = bonus.ruleId
        client_bonus.operation_date = bonus.activationDate if bonus.accruedPoints > 0 else purchases.created_date
        client_bonus.source = purchases_model.source
        client_bonus.document_id = purchases_model.purchaseId
        client_bonus.accrued_points = bonus.accruedPoints
        client_bonus.write_off_points = bonus.writeOffPoints
        client_bonus.client_purchases_id = purchases_model.purchaseId
        #client_bonus.is_active = bonus.is_activate
        client_bonus.row_number = bonus.rowNumber
        client_bonus.document_type = purchases_model.documentType
        client_bonus.expiration_date = bonus.expirationDate
        client_bonus.activation_date = bonus.activationDate
        session.add(client_bonus)
        await session.commit()
        if client_bonus.write_off_points > 0:
            await send_notification_email(
                session=session,
                event_type=EventType.points_debited_email,
                formats={
                    "client_name": client.name,
                    "cashback": client_bonus.write_off_points,
                },
                client=client
            )
            await activities.get("wb")(
                session=session,
                event_type=EventType.points_debited_whatsapp,
                #if client.activity == 'wb' else EventType.points_telegram_debited,
                client=client,
                formats={
                    "cashback": client_bonus.write_off_points
                }
            )
            # await send_template_wa(
            #     session=session,
            #     event_type=EventType.points_debited_whatsapp,
            #     client=client,
            #     formats={
            #         "cashback": client_bonus.write_off_points
            #     }
            # )
        elif client_bonus.accrued_points > 0:
            if client_p is None or len(client_p) == 0:
                await send_notification_email(
                    session=session,
                    event_type=EventType.qr_wellcome_message,
                    formats={
                        "client_name": client.name,
                        "cashback": client_bonus.accrued_points,
                        "order_number": order_number or ""
                    },
                    client=client
                )
            await send_notification_email(
                session=session,
                event_type=EventType.points_future_credit_email,
                formats={
                    "client_name": client.name,
                    "cashback": client_bonus.accrued_points,
                    "order_number": order_number or ""
                },
                client=client
            )
    #if client_bonus:

    return {
        "message": "Чек успешно записан",
        "purchaseId": purchases.id,
        "telegramId": user_id,
    }


async def add_return_purchases(
        session: AsyncSession,
        # purchase_id: str | None,
        # user_id: int | None,
        # phone: str | None,
        # products: list | None,
        # return_id: str | None,
        # order_number: int | None,
        # number: str | None,
        # shift_number: int | None,
        # ticket_print_url: str | None
        purchase_return_model: ModelClientPurchaseReturn | None,
        bonuses: typing.List[ModelClientBonus] | None
):
    user_id = None
    if not (client := await session.get(Client, purchase_return_model.telegramId)):
        client = await Client.get_client_by_phone(
            session=session,
            phone=purchase_return_model.phone
        )
    if client:
        user_id = client.id
    if not await session.get(ClientPurchase, purchase_return_model.purchaseId):
        return {
            "statusCode": 404,
            "message": f"Purchase с id {purchase_return_model.purchaseId} не найден базе",
        }

    #if purchase.return_id:
    #    return {
    #        "statusCode": 404,
    #        "message": f"Purchase с id {return_id} был уже как возвратный",
    #    }
    purchases = await ClientPurchaseReturn.get_by_purchase_id(session=session, purchase_id=purchase_return_model.purchaseId)
    if purchases:
        await session.delete(purchases)
        await session.commit()
    purchases = ClientPurchaseReturn(
        purchase_id=purchase_return_model.purchaseId,
        source=purchase_return_model.source,
        source_system=purchase_return_model.sourceSystem,
        user_id=user_id,
        products=purchase_return_model.products,
        return_id=purchase_return_model.returnId,
        order_number=purchase_return_model.orderNumber,
        number=purchase_return_model.number,
        shift_number=purchase_return_model.shiftNumber,
        ticket_print_url=purchase_return_model.ticketPrintUrl,
        site_id=purchase_return_model.siteId,
        ms_id=purchase_return_model.msId
    )
    session.add(purchases)
    await session.commit()
    await session.refresh(purchases)  # избегаем MissingGreenlet при обращении к purchases.created_date в цикле по bonus
    promo = await PromoCheckParticipation.get_promo_by_check_id(
        session=session,
        client_id=client.id,
        purchase_id=purchases.purchase_id
    )
    if promo:
        promo_contests = await PromoContests.get_active_promo(session=session)
        price_sum = 0
        for p in purchase_return_model.products:
            price_sum += p.get('sum')
        promo.amount_effective = promo.amount_effective - price_sum
        if promo.amount_effective < 25000 and datetime.now().date() <= promo_contests.date_exception.date():
            promo.annulled_at = datetime.now()
            promo.annul_reason = 'return'
            promo.status = Status.annulled
            #Ваш возврат оформлен Номер участия {promo_code} аннулирован
            await send_notification_email(
                session=session,
                event_type=EventType.promo_message_annulled,
                formats={
                    "promo_code": promo.participation_number,
                    "name": client.name
                },
                client=client
            )
    await ClientBonusPoints().delete_by_return_purchase_id(
        session=session,
        purchase_id=purchase_return_model.returnId
    )
    for bonus in bonuses:
        client_bonus = ClientBonusPoints()
        client_bonus.id = uuid.uuid4()
        client_bonus.client_id = user_id
        client_bonus.loyalty_program = bonus.rule
        client_bonus.loyalty_program_id = bonus.ruleId
        client_bonus.operation_date = bonus.activationDate if bonus.accruedPoints > 0 else purchases.created_date
        client_bonus.source = purchase_return_model.source
        client_bonus.document_id = purchase_return_model.returnId
        client_bonus.accrued_points = bonus.accruedPoints
        client_bonus.write_off_points = bonus.writeOffPoints
        client_bonus.client_purchases_id = purchase_return_model.purchaseId
        client_bonus.client_purchases_return_id = purchase_return_model.returnId
        #client_bonus.is_active = bonus.is_activate
        client_bonus.row_number = bonus.rowNumber
        client_bonus.document_type = purchase_return_model.documentType
        client_bonus.expiration_date = bonus.expirationDate
        client_bonus.activation_date = bonus.activationDate
        session.add(client_bonus)
        await session.commit()
    return {
        "statusCode": 200,
        "message": "Информация о возврате успешно записана",
        "purchaseId": purchases.purchase_id,
    }


async def get_all_client_purchases(
        session: AsyncSession,
        user_id: int
) -> Sequence[ClientPurchase]:
    stmt = select(ClientPurchase).where(
        user_id == ClientPurchase.user_id
    )
    response = await session.execute(stmt)

    return response.scalars().all()


async def get_client_purchases_by_month(
        session: AsyncSession,
        date: Optional[datetime],
        user_id: int
) -> Sequence[ClientPurchase]:
    stmt = select(ClientPurchase).where(
        (date.month == extract('month', ClientPurchase.created_date)) &
        (user_id == ClientPurchase.user_id)
    )
    response = await session.execute(stmt)

    return response.scalars().all()


async def is_return_client_purchases(
        session: AsyncSession,
        purchase_id: str,
        product_id: str,
        price: int
) -> ClientPurchaseReturn | None:
    stmt = select(ClientPurchaseReturn).where(
        ClientPurchaseReturn.purchase_id == purchase_id
    )
    response = await session.execute(stmt)
    purchases = response.scalars().all()

    for purchase in purchases:
        products = purchase.products
        for product in products:
            #product['price'] == price
            if product['id'] == product_id:
                return purchase

    return None


async def get_return_client_purchases(
        session: AsyncSession,
        purchase_id: str
) -> typing.Sequence[ClientPurchaseReturn]:
    stmt = select(ClientPurchaseReturn).where(
        ClientPurchaseReturn.purchase_id == purchase_id
    )
    response = await session.execute(stmt)
    purchases = response.scalars().all()

    return purchases
