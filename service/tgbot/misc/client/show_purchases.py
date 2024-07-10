from datetime import datetime
from typing import List
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.comands.client_purchases import (get_all_purchases,
                                                           get_purchases_by_month, is_return_purchases)


async def show_purchases(
        session: AsyncSession,
        user_id: int,
        date: datetime = None
) -> List[str]:
    all_text = []
    text = ""
    if date is not None:
        purchases = await get_purchases_by_month(
            session=session,
            date=date,
            user_id=user_id
        )
    else:
        purchases = await get_all_purchases(
            session=session,
            user_id=user_id
        )

    if purchases:
        for purchase in purchases:
            products = purchase.products
            for product in products:
                is_return = await is_return_purchases(
                    session=session,
                    purchase_id=purchase.id,
                    product_id=product['id'],
                    price=product.get('price') - product.get('discountPrice')
                )
                if not is_return:
                    if len(text) > 3500:
                        all_text.append(text)
                        text = ""
                    text += (f"Название товара: {product['name']}\n"
                             f"Количество: {product['count']}\n")
                    if product['discount']:
                        total = int(product['price'] - (product['price'] * (product['discountPercent'] / 100)))
                        text += (f"Цена: {product['price']}\n"
                                 f"Скидка: {product['discountPercent']}%\n"
                                 f"Итог скидки: {product['price'] - total}\n"
                                 f"Итого с учетом скидки: {int(product['price'] - (product['price'] * (product['discountPercent'] / 100)))}\n")
                    else:
                        text += f"Цена: {product['price']}\n"
                    text += (f"Дата покупки: {str(purchase.created_date).split(' ')[0]}\n"
                             f"Ссылка на чек: {purchase.ticket_print_url}\n\n")

    if text != "":
        all_text.append(text)
    return all_text
