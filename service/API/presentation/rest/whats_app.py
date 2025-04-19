from datetime import datetime
import typing

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse
from loguru import logger

from service.tgbot.misc.generate import generate_code
from service.API.domain.authentication import security, validate_security
from service.API.infrastructure.database.session import db_session
from service.API.infrastructure.database.models import UserTemp, User, Client
from service.API.infrastructure.models.purchases import ModelStaff
from service.API.infrastructure.utils.show_purchases import show_purchases, show_client_purchases
from service.API.infrastructure.utils.parse import parse_phone, is_valid_date
from service.API.infrastructure.database.cods import Cods
from service.API.infrastructure.utils.generate import generate_code

router = APIRouter()


@router.post("/staff/authorization", tags=["WhatsApp"], deprecated=True)
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


@router.get("/staff/get_purchases", tags=["WhatsApp"], deprecated=True)
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


@router.get("/client/get_purchases", tags=["WhatsApp"], deprecated=True)
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


@router.get(
    "/client/qr_code",
    tags=["WhatsApp"]
)
async def register_staff(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str
):
    session: AsyncSession = db_session.get()
    client = await Client.get_client_by_phone(
        session=session,
        phone=parse_phone(phone))
    code = await Cods.get_cody_by_phone(client.phone_number, session)
    if not code or (code and code.is_active) or (datetime.now() - code.created_at).total_seconds() / 60 > 15:
        code = await generate_code(session, phone_number=client.phone_number)

    return {
        'url': f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={code.code}",
        'status_code': 200
    }
