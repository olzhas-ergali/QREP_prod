import logging
import typing
from datetime import datetime
from aiogram import Bot

from typing import Sequence, Optional

from aiogram import Bot
from sqlalchemy import select, update, extract
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.models import (User, Purchase, UserTemp, PurchaseReturn, Client,
                                                        PositionDiscounts)
from service.API.infrastructure.database.vacation import StaffVacation, VacationDays


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
         (Purchase.user_id == user_id) & (datetime.now().year == extract('year', Purchase.created_date)))
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
         (datetime.now().year == extract('year', PurchaseReturn.created_date)) &
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


async def get_item_count(
        session: AsyncSession,
        user: User | None
):
    discount = None
    if user.position_id:
        discount = await get_user_discount(session, user.position_id)
    monthly_limit = 3
    discount_percentage = 30.0
    if discount:
        monthly_limit = discount.monthly_limit
        discount_percentage = discount.discount_percentage
    stmt = select(Purchase).where(
        ((datetime.now().month == extract('month', Purchase.created_date)) &
         (Purchase.user_id == user.id) & (datetime.now().year == extract('year', Purchase.created_date)))
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
                products_purchases.append(product.get('price') - product.get('discountPrice'))
                count = count + product['count']
    stmt = select(PurchaseReturn).where(
        ((datetime.now().month == extract('month', PurchaseReturn.created_date)) &
         (datetime.now().year == extract('year', PurchaseReturn.created_date)) &
         (PurchaseReturn.user_id == user.id) &
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
    available_count = monthly_limit - count
    if available_count < 0:
        available_count = 0
    return {
        "itemCount": count,
        "availableCount": available_count,
        "discountPercentage": discount_percentage
    }


async def get_user_discount(
        session: AsyncSession,
        position_id: str
):
    stmt = select(PositionDiscounts).where(position_id == PositionDiscounts.position_id)
    return await session.scalar(stmt)


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


async def add_staff_vacation(
        session: AsyncSession,
        iin: str,
        fullname: str,
        date_receipt: datetime,
        id_staff: str,
        is_fired: bool = False
):
    if is_fired:
        # vacations = await VacationDays.get_staff_vac_by_id(
        #     session=session,
        #     staff_id=staff.id
        # )
        # for v in vacations:
        #     await session.delete(v)
        # await session.delete(staff)
        # await session.commit()
        return
    if not (staff := await StaffVacation.get_by_iin(iin, session)):
        staff = StaffVacation(
            iin=iin,
            fullname=fullname,
            date_receipt=date_receipt,
            guid=id_staff
        )
    if staff.guid != id_staff:
        await session.delete(staff)
        await session.commit()
        staff = StaffVacation(
            iin=iin,
            fullname=fullname,
            date_receipt=date_receipt,
            guid=id_staff
        )
    session.add(staff)
    await session.commit()

    if not (vacation := await VacationDays.get_staff_vac_days_by_year(
            year=datetime.now().year + 1,
            staff_id=staff.id,
            session=session
    )):
        vacation = VacationDays(
            year=datetime.now().year + 1,
            staff_vac_id=staff.id,
            days=0,
            dbl_days=0
        )
        session.add(vacation)
        await session.commit()

    return staff, vacation


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
        organization_id: typing.Optional[str] = None,
        organization_name: typing.Optional[str] = None,
        organization_bin: typing.Optional[str] = None,
        position_id: typing.Optional[str] = None,
        position_name: typing.Optional[str] = None,
        bot: typing.Optional[Bot] = None
):
    now = datetime.now()
    await add_staff_vacation(
        session,
        iin,
        fullname,
        date_receipt,
        id_staff,
        date_dismissal is not None
    )
    if not (user := await session.get(UserTemp, id_staff)):
        user = UserTemp(
            id_staff=id_staff
        )
    if user_tg := await User.get_by_iin(session, user.iin):
        texts = {
            'rus': '''
🔄 *Изменение вашего статуса* 🔄

Мы заметили, что ваш статус в компании изменился.

💙 Если вы завершили работу в компании, *благодарим вас за ваш вклад и желаем успехов в новых начинаниях!* 🌟

🔄 Если у вас был перевод в другое юридическое лицо, необходимо перезапустить бота, чтобы обновить доступ:\
1️⃣ Остановите и заблокируйте бот (перейдите в настройки и нажмите нужную кнопку)\
2️⃣ Далее перезапустите бот\
3️⃣ Бот запросит ввести ИИН, пройдите авторизацию''',
            'kaz': '''
🔄 *Сіздің мәртебеңіздің өзгеруі* 🔄  

Біз сіздің компаниядағы мәртебеңіздің өзгергенін байқадық.  

💙 Егер сіз компаниядағы жұмысыңызды аяқтасаңыз, *сіздің үлесіңіз үшін алғысымызды білдіреміз және жаңа бастамаларыңызда сәттілік тілейміз!* 🌟  

🔄 Егер сіз басқа заңды тұлғаға ауыстырылған болсаңыз, қолжетімділікті жаңарту үшін ботты қайта іске қосу қажет:  
1️⃣ Ботты тоқтатыңыз және бұғаттаңыз (параметрлерге өтіп, тиісті батырманы басыңыз)  
2️⃣ Содан кейін ботты қайта іске қосыңыз  
3️⃣ Бот сізден ЖСН енгізуді сұрайды, авторизациядан өтіңіз
'''
        }
        if date_dismissal:
            user_tg.date_dismissal = date_dismissal
            user_tg.iin = None if date_dismissal.date() == now.date() else user_tg.iin
            user_tg.is_active = False if date_dismissal.date() == now.date() else True
        else:
            #user_tg.phone_number = phone
            user.name = fullname
            user_tg.organization_id = organization_id
            user_tg.organization_name = organization_name
            user_tg.position_id = position_id
            user_tg.position_name = position_name
            user_tg.organization_bin = organization_bin
        if date_dismissal.date() == now.date():
            try:
                await bot.send_message(
                    chat_id=user_tg.id,
                    text=texts.get(user_tg.local)
                )
                bot_session = await bot.get_session()
                await bot_session.close()
            except Exception as ex:
                logging.info(ex)
        session.add(user_tg)
    if c := await Client.get_client_by_phone(session=session, phone=phone):
        c.is_active = False
        c.phone_number = None
        session.add(c)
    user.phone_number = phone
    user.iin = iin
    user.name = fullname
    user.author = author
    user.date_receipt = date_receipt
    user.date_dismissal = date_dismissal
    user.update_data = datetime.today()
    user.organization_id = organization_id
    user.organization_name = organization_name
    user.position_id = position_id
    user.position_name = position_name
    user.organization_bin = organization_bin
    user.is_fired = True if date_dismissal is not None else False

    if not (discount := await get_user_discount(session=session, position_id=user.position_id)):
        discount = PositionDiscounts(
            position_id=position_id,
            position_name=position_name,
            discount_percentage=30.0,
            start_date=datetime.strptime("01.01.0001", "%d.%m.%Y"),
            end_date=datetime.strptime("31.12.9999", "%d.%m.%Y"),
            monthly_limit=3
        )
        session.add(discount)

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
