import typing
from datetime import datetime

from typing import Sequence, Optional

from sqlalchemy import select, update, extract
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.models import User, Purchase, UserTemp, PurchaseReturn


async def get_staff(
        session: AsyncSession,
        phone_number: str
):
    stmt = select(User).where(
        phone_number == User.phone_number
    )

    return await session.scalar(stmt)


async def get_purchases_count(
        session: AsyncSession,
        user_id: int
):
    stmt = select(Purchase).where(
        ((datetime.now().month == extract('month', Purchase.created_date)) &
         (Purchase.user_id == user_id))
    )
    response = await session.execute(stmt)
    purchases = response.scalars().all()
    count = 0
    products_purchases = []
    purchases_id = []
    for purchase in purchases:
        products = purchase.products
        purchases_id.append(purchase.id)
        for product in products:
            if product.get('discount'):
                # count = count - product['count'] if purchase.is_return else count + product['count']
                count = count + product['count']
                products_purchases.append(product.get('price') - product.get('discountPrice'))
    stmt = select(PurchaseReturn).where(
        ((datetime.now().month == extract('month', PurchaseReturn.created_date)) &
         (PurchaseReturn.user_id == user_id) &
         (PurchaseReturn.purchase_id.in_(purchases_id)))
    )
    response = await session.execute(stmt)
    purchases_return = response.scalars().all()
    for purchase in purchases_return:
        products = purchase.products
        for product in products:
            if product.get('price') in products_purchases:
                # count = count - product['count'] if purchase.is_return else count + product['count']
                count = count - product['count']
    if count < 0:
        count = 0
    return {
        "itemCount": count
    }


async def add_purchases(
        session: AsyncSession,
        purchase_id: str,
        user_id: int,
        phone: str,
        products: list
):
    if not user_id:
        user = await User.get_by_phone(
            session=session,
            phone=phone
        )
        user_id = user.id
    purchases = Purchase(
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
        user = await User.get_by_phone(
            session=session,
            phone=phone
        )
        user_id = user.id
    if not await session.get(Purchase, purchase_id):
        return {
            "statusCode": 404,
            "message": f"Purchase с id {purchase_id} не найден базе",
        }

    #if purchase.return_id:
    #    return {
    #        "statusCode": 404,
    #        "message": f"Purchase с id {return_id} был уже как возвратный",
    #    }

    purchases = PurchaseReturn(
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


async def add_user_temp(
        session: AsyncSession,
        user_id: typing.Optional[int],
        phone: typing.Optional[str],
        name: typing.Optional[str],
):
    user = User(
        id=user_id,
    )
    user.is_active = True
    user.author = "Test"
    user.phone_number = phone
    user.name = name
    user.date_receipt = datetime.strptime("15.01.2024", '%d.%m.%Y')
    #user.date_dismissal = datetime.strptime("20.02.2024", '%d.%m.%Y')

    session.add(user)
    await session.commit()
    return {
        "message": "Пользователь добавлен",
        "telegramId": user.id,
    }


async def add_employees(
        session: AsyncSession,
        id_staff: typing.Optional[str],
        fullname: typing.Optional[str],
        author: typing.Optional[str],
        update_date: typing.Optional[datetime],
        date_receipt: typing.Optional[datetime],
        date_dismissal: typing.Optional[datetime] = None,
        phone: typing.Optional[str] = None,
        iin: typing.Optional[str] = None,
):
    if not (user := await session.get(UserTemp, id_staff)):
        user = UserTemp(
            id_staff=id_staff
        )
    if (user_tg := await User.get_by_iin(session, user.iin)) is not None:
        if date_dismissal:
            user_tg.date_dismissal = date_dismissal
            user_tg.iin = None
            user_tg.is_active = False
            user.is_fired = True
        else:
            #user_tg.phone_number = phone
            user.name = fullname
        session.add(user_tg)
    user.phone_number = phone
    user.iin = iin
    user.name = fullname
    user.author = author
    user.date_receipt = date_receipt
    user.date_dismissal = date_dismissal
    user.update_data = update_date

    session.add(user)

    await session.commit()
    return {
        "id": id_staff,
        "message": "Сотрудник успешно создан."
    }


async def get_user(
        session: AsyncSession,
        phone: str
) -> User:
    stmt = select(User).where(
        User.phone_number == phone
    )
    return await session.scalar(stmt)


async def get_user_by_iin(
        session: AsyncSession,
        iin: str
) -> UserTemp:
    stmt = select(UserTemp).where(
        UserTemp.iin == iin
    )
    return await session.scalar(stmt)


async def get_staff_by_iin(
        session: AsyncSession,
        iin: str
) -> User:
    stmt = select(User).where(
        User.iin == iin
    )
    return await session.scalar(stmt)


async def get_all_purchases(
        session: AsyncSession,
        user_id: int
) -> Sequence[Purchase]:
    stmt = select(Purchase).where(
        user_id == Purchase.user_id
    )
    response = await session.execute(stmt)

    return response.scalars().all()


async def get_purchases_by_month(
        session: AsyncSession,
        date: Optional[datetime],
        user_id: int
) -> Sequence[Purchase]:
    stmt = select(Purchase).where(
        (date.month == extract('month', Purchase.created_date)) &
        (user_id == Purchase.user_id)
    )
    response = await session.execute(stmt)

    return response.scalars().all()


async def is_return_purchases(
        session: AsyncSession,
        purchase_id: str,
        product_id: str,
        price: int
) -> bool:
    stmt = select(PurchaseReturn).where(
        PurchaseReturn.purchase_id == purchase_id
    )
    response = await session.execute(stmt)
    purchases = response.scalars().all()

    for purchase in purchases:
        products = purchase.products
        for product in products:
            if product['id'] == product_id and product['price'] == price:
                return True

    return False
