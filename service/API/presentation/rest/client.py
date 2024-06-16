import typing
from service.API.config import settings

from aiogram import Bot
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse

from service.API.domain.authentication import security, validate_security
from service.API.infrastructure.database.session import db_session
from service.API.infrastructure.database.models import Client
from service.API.infrastructure.utils.client_notification import send_notification_from_client
from service.API.infrastructure.utils.parse import parse_phone
from service.API.infrastructure.models.client import ModelAuth


router = APIRouter()


@router.post('/client/{telegramId}/notifications')
async def get_count(
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


@router.get('/client/authorization')
async def is_authorization_client(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        authorization: ModelAuth
):
    session: AsyncSession = db_session.get()
    client = await Client.get_client_by_phone(
        session=session,
        phone=parse_phone(authorization.phone)
    )

    if client:
        return {
            "status_code": 200,
            "message": "Клиент найден"
        }
    return {
        "status_code": 404,
        "message": "Клиент не найден"
    }


@router.post('/client/authorization')
async def authorization_client(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        authorization: ModelAuth
):
    session: AsyncSession = db_session.get()
    client = Client()
    client.phone_number = parse_phone(authorization.phone)
    client.gender = authorization.gender
    client.name = authorization.clientFullName
    client.birthday_date = authorization.birthDate
    session.add(client)
    await session.commit()
    if client:
        return {
            "status_code": 200,
            "message": "Клиент авторизовался"
        }
    return {
        "status_code": 404,
        "message": "Пройзошла ошибка"
    }

