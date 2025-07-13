import typing
import uuid
from typing import Optional, Sequence
from datetime import datetime

from sqlalchemy import select, update, extract
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.models import ClientPurchase, ClientPurchaseReturn, Client
from service.API.infrastructure.database.loyalty import ClientBonusPoints
from service.API.infrastructure.models.purchases import ModelClientBonus, ModelPurchaseClient, ModelClientPurchaseReturn
from service.API.infrastructure.database.notification import MessageLog, MessageTemplate, EventType
from service.tgbot.lib.SendPlusAPI.send_plus import SendPlus
from service.API.config import settings
from service.API.infrastructure.utils.smpt import Mail


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
    if client_p is None:
        mail = Mail()
        wb = SendPlus(
            client_id=settings.wb_cred.client_id,
            client_secret=settings.wb_cred.client_secret,
            waba_bot_id=settings.wb_cred.wb_bot_id
        )
        local = await wb.get_local_by_phone(purchases_model.phone)
        template = await MessageTemplate.get_message_template(
            session=session,
            channel="Email",
            event_type=EventType.qr_enrollment_online,
            local=local,
            audience_type="client"
        )
        await mail.send_message(
            message=template.body_template.format(name=client.name, cashback="100"),
            subject=template.title_template,
            to_address=[client.email]
        )
        log = MessageLog(
            clint_id=client.id,
            channel="Email",
            event_type=EventType.qr_enrollment_online,
            local=local,
            status="Good",
            message_content=template.body_template.format(clname=client.name, cashback="100")
        )
        session.add(log)

    purchases = ClientPurchase(
        id=purchases_model.purchaseId,
        source_system=purchases_model.sourceSystem,
        user_id=user_id,
        products=purchases_model.products,
        order_number=purchases_model.orderNumber,
        number=purchases_model.number,
        shift_number=purchases_model.shiftNumber,
        ticket_print_url=purchases_model.ticketPrintUrl,
        site_id=purchases_model.siteId,
        mc_id=purchases_model.mcId
    )
    session.add(purchases)
    await session.commit()
    client_bonus = None
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
    if client_bonus and client_bonus.write_off_points > 0:
        mail = Mail()
        wb = SendPlus(
            client_id=settings.wb_cred.client_id,
            client_secret=settings.wb_cred.client_secret,
            waba_bot_id=settings.wb_cred.wb_bot_id
        )
        local = await wb.get_local_by_phone(purchases_model.phone)
        template = await MessageTemplate.get_message_template(
            session=session,
            channel="Email",
            event_type=EventType.points_debited_email,
            local=local,
            audience_type="client"
        )
        await mail.send_message(
            message=template.body_template.format(name=client.name, cashback=client_bonus.write_off_points),
            subject=template.title_template,
            to_address=[client.email]
        )
        log = MessageLog(
            clint_id=client.id,
            channel="Email",
            event_type=EventType.qr_enrollment_online,
            local=local,
            status="Good",
            message_content=template.body_template.format(name=client.name, cashback=client_bonus.write_off_points)
        )
        session.add(log)
        await session.commit()
        if purchases_model.mcId is not None:
            template_wa = await MessageTemplate.get_message_template(
                session=session,
                channel="WhatsApp",
                event_type=EventType.points_debited_whatsapp,
                local=local,
                audience_type="client"
            )
        else:
            template_wa = await MessageTemplate.get_message_template(
                session=session,
                channel="WhatsApp",
                event_type=EventType.points_debited_whatsapp_offline,
                local=local,
                audience_type="client"
            )
        await wb.send_by_phone(
            phone=client.phone_number,
            bot_id=settings.wb_cred.wb_bot_id,
            text=template_wa
        )
        log = MessageLog(
            clint_id=client.id,
            channel="WhatsApp",
            event_type=EventType.qr_enrollment_online,
            local=local,
            status="Good",
            message_content=template.body_template.format(name=client.name, cashback=client_bonus.write_off_points)
        )
        session.add(log)
        await session.commit()
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
        source_system=purchase_return_model.sourceSystem,
        user_id=user_id,
        products=purchase_return_model.products,
        return_id=purchase_return_model.returnId,
        order_number=purchase_return_model.orderNumber,
        number=purchase_return_model.number,
        shift_number=purchase_return_model.shiftNumber,
        ticket_print_url=purchase_return_model.ticketPrintUrl,
        site_id=purchase_return_model.siteId,
        mc_id=purchase_return_model.mcId
    )
    session.add(purchases)
    await session.commit()
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
) -> bool:
    stmt = select(ClientPurchaseReturn).where(
        ClientPurchaseReturn.purchase_id == purchase_id
    )
    response = await session.execute(stmt)
    purchases = response.scalars().all()

    for purchase in purchases:
        products = purchase.products
        for product in products:
            if product['id'] == product_id and product['price'] == price:
                return True

    return False
