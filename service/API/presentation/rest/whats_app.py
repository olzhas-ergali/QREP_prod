import uuid
from datetime import datetime
import typing

from fastapi import APIRouter, Depends, HTTPException,  Query
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse
import logging

from service.API.config import settings
from service.tgbot.misc.generate import generate_code
from service.API.domain.authentication import security, validate_security
from service.API.infrastructure.database.session import db_session
from service.API.infrastructure.database.models import UserTemp, User, Client
from service.API.infrastructure.models.purchases import ModelStaff, ModelClientWA
from service.API.infrastructure.utils.show_purchases import show_purchases, show_client_purchases
from service.API.infrastructure.utils.parse import parse_phone, is_valid_date
from service.API.infrastructure.database.cods import Cods
from service.API.infrastructure.database.loyalty import ClientBonusPoints
from service.API.infrastructure.utils.generate import generate_code
from service.tgbot.lib.SendPlusAPI.send_plus import SendPlus
from service.API.infrastructure.utils.smpt import Mail
from service.API.infrastructure.database.notification import MessageLog, MessageTemplate, EventType
from service.API.infrastructure.utils.client_notification import (send_notification_wa, send_notification_email,
                                                                  send_template_wa)
from service.tgbot.lib.SendPlusAPI.templates import templates

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


@router.get("/client/get_purchases", tags=["WhatsApp"])
async def get_client_purchases(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str,
        date: bool,
        local: str = "rus"
):
    session: AsyncSession = db_session.get()
    client = await Client.get_client_by_phone(
        session=session,
        phone=parse_phone(phone))
    if client:
        answer = {
            "kaz": "Сіз әлі біздің дүкеннен сауда жасамадыңыз.\n"
                   "Сайттағы тауарлармен танысып шығуыңызды ұсынамыз — qazaqrepublic.com",
            "rus": "Вы пока не совершали покупки в нашем магазине.\n"
                   "Предлагаем вам просмотреть ассортимент на сайте — qazaqrepublic.com."
        }
        if arr := await show_client_purchases(
                session=session,
                user_id=client.id,
                local=local,
                date=datetime.now() if date else None
        ):
            return {
                "status_code": 200,
                "answer": "\n".join(arr)
            }
        return {
            "status_code": 204,
            "answer": answer.get(local)
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


@router.get("/client/bonuses", tags=["WhatsApp"])
async def get_client_purchases(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone_number: str = Query(
            default=None,
            alias="phoneNumber",
            description="Телефонный номер пользователя",
            example="77077777777"
        )
):
    session: AsyncSession = db_session.get()
    client = await Client.get_client_by_phone(
        session=session,
        phone=parse_phone(phone_number))
    available_bonus = 0
    future_bonus = 0
    if client:
        client_bonuses = await ClientBonusPoints.get_all_by_client_id(session=session, client_id=client.id)
        if client_bonuses:
            total_earned = 0
            total_spent = 0
            total_future_spent = 0
            total_future_earned = 0
            for bonus in client_bonuses:
                logging.info(f"accrued_points: {bonus.accrued_points}")
                logging.info(f"write_off_points: {bonus.write_off_points}")
                if bonus.expiration_date and bonus.expiration_date.date() < datetime.now().date():
                    continue
                if datetime.now().date() >= bonus.activation_date.date():
                    total_earned += bonus.accrued_points if bonus.accrued_points else 0
                    total_spent += bonus.write_off_points if bonus.write_off_points else 0
                else:
                    total_future_earned += bonus.accrued_points if bonus.accrued_points else 0
                    total_future_spent += bonus.write_off_points if bonus.write_off_points else 0
            if total_earned > 0:
                available_bonus += total_earned
            if total_spent > 0:
                available_bonus -= total_spent
            if total_future_earned > 0:
                future_bonus += total_future_earned
            if total_future_spent > 0:
                future_bonus -= total_future_spent
            return {
                "status_code": 200,
                "bonus": available_bonus if available_bonus > 0 else 0,
                "future_bonus": future_bonus if future_bonus > 0 else 0
            }
        return {
            "status_code": 200,
            "bonus": 0,
            "future_bonus": 0
        }
    return {
        "status_code": 204,
        "answer": "Нет данных о пользователе"
    }


@router.post('/client/wa/sendMessage',
             tags=["WhatsApp"])
async def client_send_quality_grade(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        model: ModelClientWA
):
    session: AsyncSession = db_session.get()
    client = await Client.get_client_by_phone(
        session=session,
        phone=model.phoneNumber
    )
    # wb = SendPlus(
    #     client_id=settings.wb_cred.client_id,
    #     client_secret=settings.wb_cred.client_secret,
    #     waba_bot_id=settings.wb_cred.wb_bot_id
    # )
    # template = await MessageTemplate.get_message_template(
    #     session=session,
    #     channel="WhatsApp",
    #     event_type=EventType.points_debited_whatsapp,
    #     local=model.local,
    #     audience_type="client"
    # )
    # #С вашего бонусного счёта списано {cashback} кэшбека при оплате заказа {order_number}Спасибо, что выбираете Qazaq Republic 💙
    # # template.body_template.format(
    # #     cashback="100",
    # #     order_number="123")
    # res = await wb.send_by_phone(
    #     phone=model.phoneNumber,
    #     bot_id=settings.wb_cred.wb_bot_id,
    #     text=model.message
    # )
    # log = MessageLog(
    #     id=uuid.uuid4(),
    #     client_id=client.id if client else 2,
    #     channel="WhatsApp",
    #     event_type=EventType.points_debited_whatsapp,
    #     status="Good",
    #     message_content=template.body_template.format(
    #         order_number="123",
    #         cashback="100")
    # )
    # session.add(log)

    res = await send_template_wa(
        session=session,
        event_type=EventType.points_credited_whatsapp,
        client=client,
        phone_number=model.phoneNumber,
        local=model.local,
        formats={
            "cashback": 1234
        }
    )
    return {
        'status_code': status.HTTP_200_OK,
        'message': 'Сообщение отправлено',
        'res': res
    }


@router.post('/client/sendMail',
             tags=["WhatsApp"])
async def client_send_quality_grade(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        model: ModelClientWA
):
    session: AsyncSession = db_session.get()
    client = await Client.get_client_by_phone(
        session=session,
        phone=model.phoneNumber
    )
    template = await MessageTemplate.get_message_template(
        session=session,
        channel="Email",
        event_type=EventType.points_credited_email,
        local=model.local,
        audience_type="client"
    )
    mail = Mail()
    #print(template.body_template.format(name=client.name, cashback="100"))
    msg = template.body_template.format(client_name=client.name, cashback="100").encode('utf-8').strip()
    await mail.send_message(
        message=msg,
        subject=template.title_template,
        to_address=[model.email]
    )
    return {
        'status_code': status.HTTP_200_OK,
        'message': 'Сообщение отправлено'
    }
