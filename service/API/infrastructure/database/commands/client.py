import typing
from datetime import datetime

from sqlalchemy import select, update, extract
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.models import ClientPurchase, ClientPurchaseReturn, Client


async def add_purchases(
        session: AsyncSession,
        purchase_id: str,
        user_id: int,
        phone: str,
        products: list
):
    if not user_id:
        client = await Client.get_client_by_phone(
            session=session,
            phone=phone
        )
        user_id = client.id
    purchases = ClientPurchase(
        id=purchase_id,
        user_id=user_id,
        products=products
    )

    session.add(purchases)
    await session.commit()
    return {
        "message": "Чек успешно записан",
        "purchaseId": purchases.id,
        "telegramId": user_id,
    }


async def add_return_purchases(
        session: AsyncSession,
        purchase_id: str,
        user_id: int,
        phone: str,
        products: list,
        return_id: str
):
    if not user_id:
        client = await Client.get_client_by_phone(
            session=session,
            phone=phone
        )
        user_id = client.id
    if not await session.get(ClientPurchase, purchase_id):
        return {
            "statusCode": 404,
            "message": f"Purchase с id {purchase_id} не найден базе",
        }

    #if purchase.return_id:
    #    return {
    #        "statusCode": 404,
    #        "message": f"Purchase с id {return_id} был уже как возвратный",
    #    }

    purchases = ClientPurchaseReturn(
        purchase_id=purchase_id,
        user_id=user_id,
        products=products,
        return_id=return_id
    )
    session.add(purchases)
    await session.commit()
    return {
        "statusCode": 200,
        "message": "Информация о возврате успешно записана",
        "purchaseId": purchases.purchase_id,
    }

