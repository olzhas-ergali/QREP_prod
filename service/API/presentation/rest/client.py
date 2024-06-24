import typing
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
from service.API.infrastructure.database.models import Client, ClientReview
from service.API.infrastructure.utils.client_notification import send_notification_from_client
from service.API.infrastructure.utils.parse import parse_phone
from service.API.infrastructure.models.client import ModelAuth, ModelReview
from service.API.infrastructure.models.purchases import ModelPurchase, ModelPurchaseReturn


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
            "message": "Клиент найден"
        }
    return {
        "status_code": 200,
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
        purchase: ModelPurchase
):
    session: AsyncSession = db_session.get()
    return await client.add_purchases(
        purchase_id=purchase.purchaseId,
        session=session,
        user_id=purchase.telegramId if purchase.telegramId != "" else None,
        phone=purchase.phone,
        products=purchase.products
    )


@router.post('/client/purchases/return')
async def add_purchases_return_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        purchase: ModelPurchaseReturn
):
    session: AsyncSession = db_session.get()
    if purchase.returnId != '-1':
        return await client.add_return_purchases(
            purchase_id=purchase.purchaseId,
            return_id=purchase.returnId,
            user_id=purchase.telegramId if purchase.telegramId != "" else None,
            phone=purchase.phone,
            session=session,
            products=purchase.products,
        )
    else:
        return {
            "statusCode": status.HTTP_403_FORBIDDEN,
            "message": "Return id не может быть пустым",
        }


@router.get("/client/get_purchases")
async def get_client_purchases(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str
):
    pass


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
