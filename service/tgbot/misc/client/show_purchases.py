from datetime import datetime
from typing import List
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.comands.client_purchases import (get_all_purchases,
                                                           get_purchases_by_month, is_return_purchases, get_return_client_purchases)


async def show_purchases(
        session: AsyncSession,
        user_id: int,
        _,
        date: datetime = None,
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
            purchase_return = await get_return_client_purchases(
                session=session,
                purchase_id=purchase.id
            )
            return_products = []
            dates = []
            if purchase_return:
                for r in purchase_return:
                    for product in r.products:
                        return_products.append(product.get('id'))
                        dates.append(r.created_date)
            for product in products:
                # is_return = await is_return_purchases(
                #     session=session,
                #     purchase_id=purchase.id,
                #     product_id=product['id'],
                #     price=product.get('price') - product.get('discountPrice')
                # )
                #if not is_return:

                if len(text) > 3500:
                    all_text.append(text)
                    text = ""
                text += _("Название товара: {name}\nКоличество: {count}\n").format(name=product['name'],
                                                                                   count=product['count'])
                if product['discount']:
                    total = int(product['price'] - (product['price'] * (product['discountPercent'] / 100)))
                    text += _('''Цена: {price}
Скидка: {discountPercent}%
Итог скидки: {total}
Итого с учетом скидки: {totalDiscount}''').format(
                        price=product['price'],
                        discountPercent=product['discountPercent'],
                        total=product['price'] - total,
                        totalDiscount=int(product['price'] - (product['price'] * (product['discountPercent'] / 100)))
                    )
                else:
                    text += _("Цена: {price}\n").format(price=product['price'])
                if product['id'] not in return_products:
                    text += _("Дата покупки: {created_date}\nСсылка на чек: {ticket_print_url}\n\n").format(
                        created_date=str(purchase.created_date).split(' ')[0],
                        ticket_print_url=purchase.ticket_print_url
                    )
                else:
                    index = return_products.index(product['id'])
                    text += _("Дата покупки: {created_date}\nДата возврата: {return_date}\n\n").format(
                        created_date=str(purchase.created_date).split(' ')[0],
                        return_date=str(dates[index]).split(' ')[0]
                    )
                    return_products.pop(index)
                    dates.pop(index)

    if text != "":
        all_text.append(text)
    return all_text
