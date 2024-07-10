from datetime import datetime
import typing

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse
from loguru import logger

from service.API.domain.authentication import security, validate_security
from service.API.infrastructure.database.session import db_session
from service.API.infrastructure.database.models import UserTemp, User, Client
from service.API.infrastructure.models.purchases import ModelStaff
from service.API.infrastructure.utils.show_purchases import show_purchases, show_client_purchases

router = APIRouter()


@router.post("/staff/authorization")
async def register_staff(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        staffs: ModelStaff
):
    session: AsyncSession = db_session.get()

    if not (user_t := await UserTemp.get_user_by_iin(session, staffs.iin)):
        return {
            "status_code": 404,
            "error": "Employee not found",
            "message": "Вы не можете пройти регистрацию, так как не являетесь сотрудником QR"
        }
    user_staff = User()
    #user_staff.id = user.id
    #user_staff.fullname = user.fullname
    user_staff.phone_number = staffs.phone_number
    user_staff.name = user_t.name
    user_staff.date_receipt = user_t.date_receipt
    user_staff.date_dismissal = user_t.date_dismissal
    user_staff.author = user_t.author
    user_staff.is_active = True
    user_staff.iin = staffs.iin
    session.add(user_staff)
    await session.commit()
    return {
            "status_code": 200,
            "message": "Регистрация прошла успешна"
    }


@router.get("/staff/get_purchases")
async def get_purchases_staff(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        identityNumber: str,
        date: bool
):
    session: AsyncSession = db_session.get()
    user = await User.get_by_iin(session=session, iin=identityNumber)
    if user:
        if arr := await show_purchases(
            session=session,
            user_id=user.id,
            date=datetime.now() if date else None
        ):
            return {
                "status_code": 200,
                "answer": arr
            }
        return {
            "status_code": 204,
            "answer": "Нет данных"
        }
    return {
        "status_code": 204,
        "answer": "Нет данных о пользователе"
    }


@router.get("/client/get_purchases")
async def get_client_purchases(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str,
        date: bool
):
    session: AsyncSession = db_session.get()
    client = await Client.get_client_by_phone(
        session=session,
        phone=phone)
    if client:
        if arr := await show_client_purchases(
                session=session,
                user_id=client.id,
                date=datetime.now() if date else None
        ):
            return {
                "status_code": 200,
                "answer": arr
            }
        return {
            "status_code": 204,
            "answer": "Нет данных"
        }
    return {
        "status_code": 204,
        "answer": "Нет данных о пользователе"
    }
