import logging
import uuid

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from sqlalchemy.ext.asyncio import AsyncSession
from service.API.infrastructure.database.models import Client, ClientsApp
from service.API.infrastructure.database.notification import MessageLog, MessageTemplate, EventType
from service.tgbot.lib.SendPlusAPI.send_plus import SendPlus
from service.API.config import settings
from service.API.infrastructure.utils.smpt import Mail


async def send_notification_from_client(
        bot: Bot,
        user: Client
):
    review_callback = CallbackData(
        'review', 'grade', 'action'
    )
    btns = {
        5: 'Отлично',
        4: 'Хорошо',
        3: 'Удовлетворительно',
        2: 'Плохо',
        1: 'Очень плохо',
    }
    markup = InlineKeyboardMarkup()

    for key, val in btns.items():
        btn = InlineKeyboardButton(
            text=val,
            callback_data=review_callback.new(
                grade=key,
                action='review'
            )
        )
        markup.add(btn)
    await bot.send_message(
        text="Мы ценим ваше мнение и стремимся к постоянному улучшению, "
             "просим Вас оценить качество сервиса Qazaq Republic",
        chat_id=user.id,
        reply_markup=markup
    )


async def push_client_answer_operator(
        session: AsyncSession,
        bot: Bot,
        client_app: ClientsApp,
        client: Client
):
    ans_callback = CallbackData(
        "answer", "ans", 'id', 'action'
    )
    logging.info("Уведомление для клиентов по оценке работе оператора")
    text1 = {
        "kaz": "Иә",
        "rus": "Да"
    }
    text2 = {
        "kaz": "Подключить оператора",
        "rus": "Операторды қосу"
    }
    markup = InlineKeyboardMarkup().add(
        *[
            InlineKeyboardButton(
                text=text1.get(client.local),
                callback_data=ans_callback.new(
                    ans="yes",
                    id=client.id,
                    action='user_answer'
                )
            ),
            InlineKeyboardButton(
                text=text2.get(client.local),
                callback_data=ans_callback.new(
                    ans="no",
                    id=client.id,
                    action='user_answer'
                )
            )
        ]
    )
    try:
        await bot.send_message(
            chat_id=client_app.telegram_id,
            text="Ваш вопрос решен",
            reply_markup=markup
        )
        client.is_push = True
        session.add(client)
    except Exception as ex:
        logging.exception(ex)

    session_bot = await bot.get_session()
    await session_bot.close()
    await session.commit()


async def send_notification_email(
        session: AsyncSession,
        event_type: EventType,
        formats: dict,
        client: Client
):
    wb = SendPlus(
        client_id=settings.wb_cred.client_id,
        client_secret=settings.wb_cred.client_secret,
        waba_bot_id=settings.wb_cred.wb_bot_id
    )
    mail = Mail()
    local = await wb.get_local_by_phone(client.phone_number)
    logging.info(local)
    template = await MessageTemplate.get_message_template(
        session=session,
        channel="Email",
        event_type=event_type,
        local=local if local and local != "" else 'rus',
        audience_type="client"
    )
    status = "Error"
    message = "Email doesn't exist"
    if client.email:
        status = "Good"
        message = ""
        await mail.send_message(
            message=template.body_template.format(**formats),
            subject=template.title_template,
            to_address=[client.email]
        )
    log = MessageLog(
        id=uuid.uuid4(),
        client_id=client.id,
        channel="Email",
        event_type=event_type,
        status=status,
        error_message=message,
        message_content=template.body_template.format(**formats)
    )

    session.add(log)
    await session.commit()
    await session.close()


async def send_notification_wa(
        session: AsyncSession,
        event_type: EventType,
        formats: dict,
        client: Client
):
    wb = SendPlus(
        client_id=settings.wb_cred.client_id,
        client_secret=settings.wb_cred.client_secret,
        waba_bot_id=settings.wb_cred.wb_bot_id
    )
    local = await wb.get_local_by_phone(client.phone_number)
    logging.info(local)
    template_wa = await MessageTemplate.get_message_template(
        session=session,
        channel="WhatsApp",
        event_type=event_type,
        local=local if local and local != "" else 'rus',
        audience_type="client"
    )

    message = ""
    status = "Good"
    try:
        #order_number=purchases.mc_id if purchases.mc_id else purchases.ticket_print_url, cashback=client_bonus.write_off_points
        result = await wb.send_by_phone(
            phone=client.phone_number,
            bot_id=settings.wb_cred.wb_bot_id,
            text=template_wa.body_template.format(**formats)
        )
        if result.get("status_code") == 400:
            message = "Номер телефона не активен 24ч"
            status = "Error"
    except Exception as ex:
        message = ex
        status = "Error"
    log = MessageLog(
        id=uuid.uuid4(),
        client_id=client.id if client else 412249576,
        channel="WhatsApp",
        event_type=event_type,
        status=status,
        error_message=message,
        message_content=template_wa.body_template.format(**formats)
    )
    session.add(log)
    await session.commit()
    await session.close()


async def send_template_wa(
        session: AsyncSession,
        event_type: EventType,
        formats: dict,
        client: Client
):
    wb = SendPlus(
        client_id=settings.wb_cred.client_id,
        client_secret=settings.wb_cred.client_secret,
        waba_bot_id=settings.wb_cred.wb_bot_id
    )
    local = await wb.get_local_by_phone(client.phone_number)
    logging.info(local)
    template_wa = await MessageTemplate.get_message_template(
        session=session,
        channel="WhatsApp",
        event_type=event_type,
        local=local if local and local != "" else 'rus',
        audience_type="client"
    )
    template = template_wa.body_template
    for key, val in formats.items():
        template = template.replace("%" + key + "%", str(val))
    message = ""
    status = "Good"
    logging.info(template)
    try:
        result = await wb.send_template_by_phone(
            phone=client.phone_number,
            bot_id=settings.wb_cred.wb_bot_id,
            template=template
        )
        if result.get("status_code") == 400:
            message = "Номер телефона не активен 24ч"
            status = "Error"
    except Exception as ex:
        message = ex
        status = "Error"
    log = MessageLog(
        id=uuid.uuid4(),
        client_id=client.id if client else 412249576,
        channel="WhatsApp",
        event_type=event_type,
        status=status,
        error_message=message,
        message_content=local
    )
    session.add(log)
    await session.commit()
    await session.close()
    