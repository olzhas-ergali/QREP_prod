import typing
from datetime import datetime
from typing import List
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.comands.get_purchases import (get_all_purchases,
                                                        get_purchases_by_month, is_return_purchases)


async def show_purchases(
        session: AsyncSession,
        user_id: int,
        _: typing.Callable[[str], str],
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
    main_text = _("Название товара: {name}\nКоличество: {count}\n")

    discount_text = _('''Цена: {price}
Скидка: {discount_procent}%
Итог скидки: {total_discount}
Итого с учетом скидки: {total_with_discount}\n''')
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
                    text += main_text.format(count=product['count'], name=product['name'])
                    if product['discount']:
                        total = int(product['price'] - (product['price'] * (product['discountPercent'] / 100)))
                        text += discount_text.format(
                            price=product['price'],
                            discount_procent=product['discountPercent'],
                            total_discount=product['price'] - total,
                            total_with_discount=int(product['price'] - (product['price'] * (product['discountPercent'] / 100)))
                        )
                    else:
                        text += _("Цена: {price}\n").format(price=product['price'])
                    text += _("Дата покупки: {date}\n\n").format(date=str(purchase.created_date).split(' ')[0])
    if text != "":
        all_text.append(text)
    return all_text
