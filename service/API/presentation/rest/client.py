import typing
import datetime
from service.API.config import settings

from aiogram import Bot
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse

from service.API.domain.authentication import security, validate_security
from service.API.infrastructure.database.commands import client
from service.API.infrastructure.database.session import db_session
from service.API.infrastructure.database.models import Client, ClientReview, ClientsApp, ClientMailing
from service.API.infrastructure.utils.client_notification import (send_notification_from_client,
                                                                  push_client_answer_operator)
from service.API.infrastructure.utils.parse import parse_phone
from service.API.infrastructure.models.client import ModelAuth, ModelReview, ModelLead
from service.API.infrastructure.models.purchases import (ModelPurchase, ModelPurchaseReturn,
                                                         ModelPurchaseClient, ModelClientPurchaseReturn)
from service.API.infrastructure.utils.check_client import check_user_exists
from service.tgbot.lib.bitrixAPI.leads import Leads
from service.tgbot.data.faq import grade_text

router = APIRouter()


@router.post('/client/{telegramId}/notifications')
async def client_notification(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        telegramId: int
):
    session: AsyncSession = db_session.get()
    bot = Bot(token=settings.tg_bot.bot_token, parse_mode='HTML')
    if client := await session.get(Client, telegramId):
        await send_notification_from_client(
            bot=bot,
            user=client
        )
        return {
            "status_code": 200,
            "message": "Уведомления отправлено"
        }
    return {
        "status_code": 404,
        "message": "Клиень с таким telegramId не найден"
    }


@router.get('/client/{phone}/activity')
async def get_client_activity(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str
):
    session: AsyncSession = db_session.get()
    client = await Client.get_client_by_phone(
        session=session,
        phone=parse_phone(phone)
    )
    if client.activity == "telegram":
        return {
            "status_code": 200,
            "answer": "telegram"
        }
    else:
        return {
            "status_code": 200,
            "answer": "wb"
        }


@router.post("/client/set_activity")
async def get_client_activity(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        authorization: ModelAuth
):
    session: AsyncSession = db_session.get()
    client = await Client.get_client_by_phone(
        session=session,
        phone=parse_phone(authorization.phone)
    )
    if client:
        client.activity = "wb"
        session.add(client)
        await session.commit()
        return {
            "status_code": 200
        }
    return {
        "status_code": 200,
        "error": "Клиент не найден"
    }


@router.get('/client/authorization')
async def is_authorization_client(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str
):
    session: AsyncSession = db_session.get()
    client = await Client.get_client_by_phone(
        session=session,
        phone=parse_phone(phone)
    )

    if client:
        return {
            "status_code": 200,
            "clientFullName": client.name,
            "birthDate": client.birthday_date,
            "gender": client.gender,
            "message": "Клиент найден",
            "activity": client.activity
        }
    return {
        "status_code": 204,
        "message": "Клиент с указанным номером не найден."
    }


@router.post('/client/authorization')
async def authorization_client(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        authorization: ModelAuth
):
    session: AsyncSession = db_session.get()
    try:
        client = Client()
        client.phone_number = parse_phone(authorization.phone)
        client.gender = authorization.gender
        client.name = authorization.clientFullName
        client.birthday_date = authorization.birthDate
        client.activity = "wb"
        session.add(client)
        await session.commit()

        return {
            "status_code": 200,
            "message": "Клиент авторизовался"
        }
    except Exception as ex:
        print(ex)
        return {
            "status_code": 404,
            "message": "Пройзошла ошибка",
            "error": ex
        }


@router.post('/client/purchases')
async def add_purchases_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        purchase: ModelPurchaseClient
):
    session: AsyncSession = db_session.get()
    try:
        print(purchase.telegramId)
        return await client.add_purchases(
            purchase_id=purchase.purchaseId,
            session=session,
            user_id=purchase.telegramId if purchase.telegramId != -1 else None,
            phone=purchase.phone,
            products=purchase.products,
            order_number=purchase.orderNumber,
            number=purchase.number,
            shift_number=purchase.shiftNumber,
            ticket_print_url=purchase.ticketPrintUrl
        )
    except Exception as ex:
        print(ex)


@router.post('/client/purchases/return')
async def add_purchases_return_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        purchase: ModelClientPurchaseReturn
):
    session: AsyncSession = db_session.get()
    if purchase.returnId != '-1':
        return await client.add_return_purchases(
            purchase_id=purchase.purchaseId,
            return_id=purchase.returnId,
            user_id=purchase.telegramId if purchase.telegramId != -1 else None,
            phone=purchase.phone,
            session=session,
            products=purchase.products,
            order_number=purchase.orderNumber,
            number=purchase.number,
            shift_number=purchase.shiftNumber,
            ticket_print_url=purchase.ticketPrintUrl
        )
    else:
        return {
            "statusCode": status.HTTP_403_FORBIDDEN,
            "message": "Return id не может быть пустым",
        }


@router.post("/client/reviews")
async def add_client_review(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        review: ModelReview
):
    session: AsyncSession = db_session.get()
    grades = {
        5: 'Отлично',
        4: 'Хорошо',
        3: 'Удовлетворительно',
        2: 'Плохо',
        1: 'Очень плохо',
    }
    c = await Client.get_client_by_phone(
        session=session,
        phone=review.phone
    )
    r = ClientReview()
    r.client_grade = review.grade
    r.client_review = review.review
    r.client_grade_str = grades.get(review.grade)
    r.client_id = c.id
    session.add(r)
    await session.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "message": "Отзыв добавлен"
    }


@router.post("/client/operator/notification")
async def add_client_operator_grade(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str,
        telegram_id: str = None
):
    session: AsyncSession = db_session.get()
    bot = Bot(token=settings.tg_bot.bot_token, parse_mode='HTML')

    c = await Client.get_client_by_phone(session=session, phone=phone)
    app = None
    if c and await check_user_exists(c.id, bot):
        app = await ClientsApp.get_last_app(session=session, telegram_id=c.id)
    elif c:
        app = await ClientsApp.get_last_app_by_phone(session=session, phone=phone)

    if app:
        if c.activity == 'telegram':
            await push_client_answer_operator(session=session, client=app, bot=bot)
        else:
            pass
        return {
            "status_code": status.HTTP_200_OK,
            "message": "Уведомление отправлено"
        }
    else:
        return {
            "status_code": status.HTTP_200_OK,
            "message": f"Пользователь с {phone} не найден в базе"
        }


@router.post("/client/mailing")
async def client_mailing(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str
):
    session: AsyncSession = db_session.get()
    c = await Client.get_client_by_phone(session=session, phone=phone)
    if c:
        if not ClientMailing.get_by_phone_number(
            phone=c.phone_number,
            session=session
        ):
            mailing = ClientMailing(
                telegram_id=c.id,
                phone=c.phone_number
            )
            session.add(mailing)
            await session.commit()
        return {
            "status_code": status.HTTP_200_OK,
            "find": True,
            "message": "Вы подписались на уведомление"
        }
    return {
        "status_code": status.HTTP_200_OK,
        "find": False,
        "message": f"Пользователь с {phone} не найден в базе"
    }


@router.post("/client/bitrix/lead")
async def client_create_lead(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        operator: ModelLead
):
    session: AsyncSession = db_session.get()
    c = await Client.get_client_by_phone(session=session, phone=operator.phone)
    now_date = datetime.datetime.now()
    date = now_date + datetime.timedelta(minutes=int(operator.waiting_time))
    if c:
        if not (client_app := await ClientsApp.get_last_app_by_phone(
                session=session,
                phone=operator.phone
        )):
            resp = await Leads(
                user_id=settings.bitrix.user_id,
                basic_token=settings.bitrix.token
            ).create(
                fields={
                    "FIELDS[TITLE]": "Заявка с What'sApp",
                    "FIELDS[NAME]": c.name,
                    "FIELDS[PHONE][0][VALUE]": c.phone_number,
                    "FIELDS[PHONE][0][VALUE_TYPE]": "WORKMOBILE",
                    "FIELDS[UF_CRM_1733080465]": "",
                    "FIELDS[UF_CRM_1733197853]": now_date.strftime("%d.%m.%Y %H:%M:%S"),
                    "FIELDS[UF_CRM_1733197875]": date.strftime("%d.%m.%Y %H:%M:%S"),
                    "FIELDS[UF_CRM_1731574397751]": operator.tag,
                    "FIELDS[IM][0][VALUE]": "What'sApp",
                    "FIELDS[IM][0][VALUE_TYPE]": "What'sApp",
                    "FIELDS[BIRTHDATE]": c.birthday_date.strftime("%d.%m.%Y %H:%M:%S")
                }
            )
            client_app = ClientsApp(
                id=resp.get('result'),
                waiting_time=date,
                phone_number=c.phone_number
            )
            session.add(client_app)
            await session.commit()
            return {
                "status_code": status.HTTP_200_OK,
                "find": True,
                "create": True,
                "message": '''
Спасибо за выбор! Оператор свяжется с вами в указанное время.

Таңдағаныңыз үшін рақмет! Оператор сізбен көрсетілген уақытта хабарласады.
'''
            }
        return {
            "status_code": status.HTTP_200_OK,
            "find": True,
            "create": False,
            "message": '''
Вы уже подавали заявку, подождите пока оператор ответит на ваш запрос

Сіз өтініш жібердіңіз, оператор сұрауыңызға жауап бергенше күтіңіз
'''
        }
    return {
        "status_code": status.HTTP_200_OK,
        "find": False,
        "create": False,
        "message": f"Пользователь с {operator.phone} не найден в базе"
    }


@router.patch("/client/bitrix/lead")
async def client_create_lead(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        operator: ModelLead,
        lead_id: str
):
    session: AsyncSession = db_session.get()
    c = await Client.get_client_by_phone(session=session, phone=operator.phone)

    if c:
        await Leads(
            user_id=settings.bitrix.user_id,
            basic_token=settings.bitrix.token
        ).update(
            fields={
                "ID": lead_id,
                "FIELDS[UF_CRM_1731932281238]": operator.grade
            }
        )
        return {
            "status_code": status.HTTP_200_OK,
            "find": True,
            "update": True,
            "message": grade_text.get(operator.grade in ['1', '2', '3'])
        }

    return {
        "status_code": status.HTTP_200_OK,
        "find": False,
        "update": False,
        "message": f"Пользователь с {operator.phone} не найден в базе"
    }
