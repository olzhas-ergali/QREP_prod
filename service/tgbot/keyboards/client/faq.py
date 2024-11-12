import typing

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from service.tgbot.keyboards import generate
from service.tgbot.keyboards.query_cb import FaqCallback, FaqNewCallback
from service.tgbot.data.faq import faq_texts_new


async def get_faq_ikb(
        faq_lvl: dict,
        chapter: str = None,
        btn_lvl: int = 0
):
    markup = InlineKeyboardMarkup(1)
    lvl = {
        0: ['Оформление заказа',
            'Редактирование данных пользователя',
            'Восстановление пароля',
            'Просмотр сделанных заказов',
            'Возврат и обмен товара',
            'Доставка',
            'Оплата'
            ],
        1: ['Как оформить заказ на сайте',
            'Как найти номер заказа',
            'Как изменить свои данные',
            'Как восстановить пароль',
            'Как посмотреть сделанный заказ',
            'Условия обмена/возврата',
            'Когда вернут средства',
            'Как получить трекинг номер',
            'Условия доставки',
            'Когда приедет заказ',
            'Не проходит оплата при оформлении',
            'Оплата каспи кредит/ред',
            ],
        2: ["Каз", "Рус"]
    }
    print(btn_lvl, chapter)
    print()
    if btn_lvl < 3:
        for i, (key, value) in enumerate(faq_lvl.items()):

            try:
                btn = InlineKeyboardButton(
                    text=lvl.get(btn_lvl)[i],
                    callback_data=FaqCallback.new(
                        chapter=key,
                        lvl=btn_lvl+1,
                        action='faq'
                    )
                )
                markup.add(btn)
            except Exception as ex:
                print(ex)

    if btn_lvl > 0:
        if btn_lvl - 1 == 0:
            chapter = str(None)
        btn = InlineKeyboardButton(
            text="Назад",
            callback_data=FaqCallback.new(
                chapter=chapter,
                lvl=btn_lvl - 1,
                action='faq'
            )
        )
        markup.add(btn)
    return markup


async def get_faq_btns_new(
        curr_items=None
):
    markup = InlineKeyboardMarkup()
    #keys = list(faq_texts_new.keys())
    items = curr_items
    #print(items)
    if not isinstance(items, str):
        for i, (k, v) in enumerate(items.items()):
            #print(f"key: {k}", f"val: {v}")
            if k == "rus":
                k = "На русском"
            if k == "kaz":
                k = "На казахском"
            btn = InlineKeyboardButton(
                text=k,
                callback_data=FaqNewCallback.new(
                    chapter=i,
                    action='faq'
                )
            )
            markup.add(btn)
        if curr_items and curr_items != faq_texts_new:
            btn = InlineKeyboardButton(
                text="Назад",
                callback_data=FaqNewCallback.new(
                    chapter="back",
                    action='faq'
                )
            )
            markup.add(btn)
        return markup, curr_items

    return items, {}
