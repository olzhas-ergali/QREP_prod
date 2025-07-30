from datetime import datetime
from typing import List
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.commands.staff import (get_all_purchases,
                                                                get_purchases_by_month, is_return_purchases)
from service.API.infrastructure.database.commands.client import (get_all_client_purchases,
                                                                 get_client_purchases_by_month,
                                                                 is_return_client_purchases,
                                                                 get_return_client_purchases)


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
                    if len(text) > 800:
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
                    text += f"Дата покупки: {str(purchase.created_date).split(' ')[0]}\n\n"
    if text != "":
        all_text.append(text)
    return all_text


async def show_client_purchases(
        session: AsyncSession,
        user_id: int,
        local: str,
        date: datetime = None
) -> List[str]:
    all_text = []
    text = ""

    local_texts = {
        "kaz": {
            "Название товара": "Өнім атауы",
            "Количество": "Саны",
            "Цена": "Бағасы",
            "Скидка": "Жеңілдік",
            "Итог скидки": "Жалпы жеңілдік",
            "Итого с учетом скидки": "Жеңілдікпен қоса барлығы",
            "Дата покупки": "Сатып алу күні",
            "Ссылка на чек": "Түбіртек сілтемесі",
            "Дата возврата": "Тауар қайтару күні"
        }
    }
    local_texts = local_texts.get(local, {})
    if date is not None:
        purchases = await get_client_purchases_by_month(
            session=session,
            date=date,
            user_id=user_id
        )
    else:
        purchases = await get_all_client_purchases(
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
            if purchase_return:
                for r in purchase_return:
                    for product in r.products:
                        return_products.append(product.get('id'))
            for product in products:
                # purchase_return = await is_return_client_purchases(
                #     session=session,
                #     purchase_id=purchase.id,
                #     product_id=product['id'],
                #     price=product.get('price') - product.get('discountPrice')
                # )
                # if not is_return:

                if len(text) > 800:
                    all_text.append(text)
                    text = ""

                text += (f"{local_texts.get('Название товара', 'Название товара')}: {product['name']}\n"
                         f"{local_texts.get('Количество', 'Количество')}: {product['count']}\n")
                if product['discount']:
                    total = int(product['price'] - (product['price'] * (product['discountPercent'] / 100)))
                    text += (f"{local_texts.get('Цена', 'Цена')}: {product['price']}\n"
                             f"{local_texts.get('Скидка', 'Скидка')}: {product['discountPercent']}%\n"
                             f"{local_texts.get('Итог скидки', 'Итог скидки')}: {product['price'] - total}\n"
                             f"{local_texts.get('Итого с учетом скидки', 'Итого с учетом скидки')}: {int(product['price'] - (product['price'] * (product['discountPercent'] / 100)))}\n")
                else:
                    text += f"{local_texts.get('Цена', 'Цена')}: {product['price']}\n"
                if product['id'] not in return_products:
                    text += (
                        f"{local_texts.get('Дата покупки', 'Дата покупки')}: {str(purchase.created_date).split(' ')[0]}\n"
                        f"{local_texts.get('Ссылка на чек', 'Ссылка на чек')}: {purchase.ticket_print_url if purchase.ticket_print_url else ''}\n\n")
                else:
                    return_products.pop(return_products.index(product['id']))
                    text += (
                        f"{local_texts.get('Дата покупки', 'Дата покупки')}: {str(purchase.created_date).split(' ')[0]}\n"
                        f"{local_texts.get('Дата возврата', 'Дата возврата')}: {str(purchase_return.created_date).split(' ')[0]}\n\n")

    if text != "":
        all_text.append(text)
    return all_text

