import typing

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from service.tgbot.keyboards import generate
from service.tgbot.keyboards.query_cb import (
    FaqCallback,
    FaqNewCallback,
    MailingsNewCallback,
    OperatorCallback,
    AnswerCallback)
from service.tgbot.data.faq import faq_texts2


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
    if isinstance(items, list):
        markup.add(
            InlineKeyboardButton(
                text="Да/Иә",
                callback_data=MailingsNewCallback.new(
                    answer="yes",
                    action='mailing'
                )
            )
        )
        markup.add(
            InlineKeyboardButton(
                text="Нет/Жоқ",
                callback_data=MailingsNewCallback.new(
                    answer="no",
                    action='mailing'
                )
            )
        )
        markup.add(
            InlineKeyboardButton(
                text="Назад",
                callback_data=FaqNewCallback.new(
                    chapter="back",
                    action='faq'
                )
            )
        )
        return markup, items[0]
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

    if curr_items and curr_items != faq_texts2:
        btn = InlineKeyboardButton(
            text="Назад",
            callback_data=FaqNewCallback.new(
                chapter="back",
                action='faq'
            )
        )
        markup.add(btn)

    return markup, curr_items


async def get_times():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        *[
            InlineKeyboardButton(
                text="Сейчас/Дәл қазір",
                callback_data=OperatorCallback.new(
                    time="0",
                    action='application'
                )
            ),
            InlineKeyboardButton(
                text="Через 30 минут/30 минуттан кейін",
                callback_data=OperatorCallback.new(
                    time="30",
                    action='application'
                )
            ),
            InlineKeyboardButton(
                text="Через 1 час/1 сағаттан кейін",
                callback_data=OperatorCallback.new(
                    time="60",
                    action='application'
                )
            ),
            InlineKeyboardButton(
                text="Через 2 час/2 сағаттан кейін",
                callback_data=OperatorCallback.new(
                    time="120",
                    action='application'
                )
            )
        ]
    )

    return markup


def get_answer():
    return InlineKeyboardMarkup().add(
        *[
            InlineKeyboardButton(
                text="Да",
                callback_data=AnswerCallback.new(
                    ans="yes",
                    action='user_answer'
                )
            ),
            InlineKeyboardButton(
                text="Подключить оператора",
                callback_data=AnswerCallback.new(
                    ans="no",
                    action='user_answer'
                )
            )
        ]
    )


def get_grade_btns():
    return InlineKeyboardMarkup(row_width=1).add(
        *[
            InlineKeyboardButton(
                text="1",
                callback_data=AnswerCallback.new(
                    ans="1",
                    action='user_grade'
                )
            ),
            InlineKeyboardButton(
                text="2",
                callback_data=AnswerCallback.new(
                    ans="2",
                    action='user_grade'
                )
            ),
            InlineKeyboardButton(
                text="3",
                callback_data=AnswerCallback.new(
                    ans="3",
                    action='user_grade'
                )
            ),
            InlineKeyboardButton(
                text="4",
                callback_data=AnswerCallback.new(
                    ans="4",
                    action='user_grade'
                )
            ),
            InlineKeyboardButton(
                text="5",
                callback_data=AnswerCallback.new(
                    ans="5",
                    action='user_grade'
                )
            )
        ]
    )
