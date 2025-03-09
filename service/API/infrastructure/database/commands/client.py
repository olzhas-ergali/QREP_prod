from typing import Optional, Sequence
from datetime import datetime

from sqlalchemy import select, update, extract
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.models import ClientPurchase, ClientPurchaseReturn, Client


async def add_purchases(
        session: AsyncSession,
        purchase_id: str,
        user_id: int | None,
        phone: str | None,
        products: list | None,
        order_number: int | None,
        number: str | None,
        shift_number: int | None,
        ticket_print_url: str | None
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
        products=products,
        order_number=order_number,
        number=number,
        shift_number=shift_number,
        ticket_print_url=ticket_print_url
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
        purchase_id: str | None,
        user_id: int | None,
        phone: str | None,
        products: list | None,
        return_id: str | None,
        order_number: int | None,
        number: str | None,
        shift_number: int | None,
        ticket_print_url: str | None
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
        return_id=return_id,
        order_number=order_number,
        number=number,
        shift_number=shift_number,
        ticket_print_url=ticket_print_url
    )
    session.add(purchases)
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
