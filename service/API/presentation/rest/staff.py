import typing
from service.API.config import settings

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse
from aiogram import Bot

from service.API.domain.authentication import security, validate_security
from service.API.infrastructure.utils.check_client import check_user_exists
from service.API.infrastructure.utils.parse import parse_phone
from service.API.infrastructure.database.commands import staff
from service.API.infrastructure.database.session import db_session
from service.API.infrastructure.models.purchases import ModelUserTemp
from service.API.infrastructure.database.models import Client

router = APIRouter()


@router.get('/authorization')
async def add_user_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone_number: str
):
    session: AsyncSession = db_session.get()
    user = await staff.get_user(
        session=session,
        phone=phone_number
    )
    if user:
        #print(user.iin)
        return {
            "message": "Сотрудник найден",
            "userFullName": user.name,
            "telegramId": user.id,
            "isActive": user.is_active
        }
    return {
        "message": "Сотрудник не найден",
    }


@router.get('/v2/authorization')
async def get_user_info_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone_number: str
):
    session: AsyncSession = db_session.get()
    bot = Bot(token=settings.tg_bot.bot_token, parse_mode='HTML')
    client = await Client.get_client_by_phone(
        session=session,
        phone=parse_phone(phone_number)
    )

    user = await staff.get_user(
        session=session,
        phone=phone_number
    )
    if user:
        return {
            "status_code": 200,
            "message": "Сотрудник найден",
            "userFullName": user.name,
            "telegramId": user.id,
            "isActive": user.is_active,
            "isStaff": True
        }

    elif client:
        return {
            "status_code": 200,
            "clientFullName": client.name,
            "birthDate": client.birthday_date,
            "gender": client.gender,
            "message": "Клиент найден",
            "telegramId": client.id if await check_user_exists(client.id, bot) else None,
            "activity": client.activity,
            "isStaff": False
        }

    return {
        "status_code": 404,
        "message": "Пользователь с указанным номером не найден."
    }


@router.post('/api/employees')
async def employees_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        user: ModelUserTemp
):
    session: AsyncSession = db_session.get()

    try:
        return await staff.add_employees(
            session=session,
            id_staff=user.idStaff,
            fullname=user.userFullName,
            phone=user.phone,
            author=user.author,
            update_date=user.updateDate,
            date_receipt=user.dateOfReceipt,
            date_dismissal=user.dateOfDismissal,
            iin=user.iin
        )
    except Exception as ex:
        return {
            'status_code': status.HTTP_400_BAD_REQUEST,
            "error": "Некорректные данные. Проверьте переданные параметры."
        }


@router.get('/identityNumber')
async def get_user_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        identityNumber: str
):
    session: AsyncSession = db_session.get()
    user = await staff.get_staff_by_iin(
        session=session,
        iin=identityNumber
    )
    if user:
        return {
            "status_code": 200,
            "message": "Сотрудник найден",
            #"idStaff": user.id_staff,
            "phoneNumber": user.phone_number,
            "userFullName": user.name,
            "author": user.author,
            "dataReceipt": user.date_receipt,
            "dateDismissal": user.date_dismissal,
            "createdAt": user.created_at,
            #"updateDate": user.update_data,
            #"isFired": user.is_fired,
            "isActive": user.is_active
        }
    return {
        "status_code": 404,
        "error": "Employee not found",
        "message": "Сотрудник с указанным идентификационным номером не найден"
    }


@router.get('/phoneNumber')
async def get_user_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str
):
    session: AsyncSession = db_session.get()
    user = await staff.get_user(
        session=session,
        phone=phone
    )
    if user:
        return {
            "status_code": 200,
            "message": "Сотрудник найден",
            "identityNumber": user.iin,
            "phoneNumber": user.phone_number,
            "userFullName": user.name,
            "author": user.author,
            "dataReceipt": user.date_receipt,
            "dateDismissal": user.date_dismissal,
            "createdAt": user.created_at,
            "isActive": user.is_active
        }
    return {
        "status_code": 404,
        "error": "Employee not found",
        "message": "Сотрудник с указанным идентификационным номером не найден"
    }
