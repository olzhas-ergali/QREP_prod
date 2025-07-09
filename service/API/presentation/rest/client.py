import typing
import datetime
import re
import regex
import logging

from service.API.config import settings

from aiogram import Bot
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, asc
from starlette import status
from starlette.responses import RedirectResponse

from service.API.infrastructure.database.cods import Cods
from service.API.domain.authentication import security, validate_security
from service.API.infrastructure.database.commands import client
from service.API.infrastructure.database.session import db_session
from service.API.infrastructure.database.models import Client, ClientReview, ClientsApp, ClientMailing
from service.API.infrastructure.utils.client_notification import (send_notification_from_client,
                                                                  push_client_answer_operator)
from service.API.infrastructure.utils.parse import parse_phone, is_valid_date, parse_date
from service.API.infrastructure.models.client import ModelAuth, ModelReview, ModelLead, ModelAuthSite, ModelTemplate
from service.API.infrastructure.models.purchases import (ModelPurchase, ModelPurchaseReturn,
                                                         ModelPurchaseClient, ModelClientPurchaseReturn)
from service.API.infrastructure.database.notification import MessageTemplate, EventType
from service.API.infrastructure.database.loyalty import ClientBonusPoints, BonusExpirationNotifications
from service.API.infrastructure.database.models import ClientPurchase, ClientPurchaseReturn
from service.API.infrastructure.utils.check_client import check_user_exists
from service.tgbot.lib.bitrixAPI.leads import Leads
from service.tgbot.data.faq import grade_text, grade_text_kaz
from service.tgbot.lib.SendPlusAPI.send_plus import SendPlus
from service.tgbot.lib.SendPlusAPI.templates import templates
from service.API.infrastructure.utils.generate import generate_code
from service.API.infrastructure.utils.types import Sort, Order

router = APIRouter()


@router.post('/client/{telegramId}/notifications',
             tags=['client'],
             description="Отправка уведомление клиенту по телеграм id")
async def client_notification(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        telegramId: int
):
    session: AsyncSession = db_session.get()
    bot = Bot(token=settings.tg_bot.bot_token, parse_mode='HTML')
    c: Client | None = await session.get(Client, telegramId)
    if client is not None:
        await send_notification_from_client(
            bot=bot,
            user=c
        )
        return {
            "status_code": 200,
            "message": "Уведомления отправлено"
        }
    return {
        "status_code": 404,
        "message": "Клиень с таким telegramId не найден"
    }


@router.get('/client/{phone}/activity',
            tags=['client'],
            description="Получение активности пользовтаеля")
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


@router.post("/client/set_activity",
             tags=['client'],
             description="Изменение активности клиента")
async def set_client_activity(
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


@router.get('/client/authorization',
            tags=['client'],
            description="Проверка есть ли такой клиента")
async def is_authorization_client(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str = Query(
            alias="phone",
            description="Телефонный номер пользователя",
            example="77077777777"
        )
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
            "activity": client.activity,
            # "local": client.local
        }
    return {
        "status_code": 204,
        "message": "Клиент с указанным номером не найден."
    }


@router.post('/client/authorization',
             tags=['client'],
             description="Авторизация клиента")
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
#        client.local = authorization.local
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


@router.post('/client/purchases',
             tags=['client'],
             description="Добавляет данные о покупках")
async def add_purchases_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        purchase: ModelPurchaseClient
):
    session: AsyncSession = db_session.get()
    try:
        print(purchase.telegramId)
        return await client.add_purchases(
            session=session,
            bonuses=purchase.bonus,
            purchases_model=purchase
        )
    except Exception as ex:
        logging.info(ex)
        return HTTPException(detail=ex, status_code=500)


@router.post('/client/purchases/return',
             tags=['client'],
             summary="Добавляет данные о возвратных покупках")
async def add_purchases_return_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        purchase: ModelClientPurchaseReturn
):
    session: AsyncSession = db_session.get()
    if purchase.returnId != '-1':
        return await client.add_return_purchases(
            session=session,
            purchase_return_model=purchase,
            bonuses=purchase.bonus
        )
    else:
        return {
            "statusCode": status.HTTP_403_FORBIDDEN,
            "message": "Return id не может быть пустым",
        }


@router.get("/api/v1/clients/bonus-points")
async def get_bonus_points(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone_number: str = Query(
            default=None,
            alias="phoneNumber",
            description="Телефонный номер пользователя",
            example="77077777777"
        ),
        client_id: int = Query(
            default=None,
            alias="clientId",
            description="Id клиента",
            example=123456
        )
):
    session: AsyncSession = db_session.get()
    if not (client_b := await Client.get_client_by_phone(session=session, phone=phone_number)):
        client_b = await session.get(Client, client_id)
    if not client_b:
        return HTTPException(status_code=204, detail="Client not found")
    logging.info(client_b.id)
    client_bonuses = await ClientBonusPoints.get_by_client_id(
        session=session,
        client_id=client_b.id,
        sort=ClientBonusPoints.expiration_date
    )
    total_earned = 0
    total_spent = 0
    available_bonus = 0
    soon_expiring = []
    expired_bonus = 0
    logging.info(f"ClinetID -> {client_b.phone_number}")
    logging.info(f"Lens -> {len(client_bonuses)}")
    for bonus in client_bonuses:
        logging.info(f"BonusActivationDate -> {bonus.activation_date}")
        #accrued_points = bonus.accrued_points if bonus.accrued_points > 0 else 0
        #write_off_points = bonus.write_off_points if bonus.write_off_points > 0 else 0
        logging.info(f"accrued_points: {bonus.accrued_points}")
        logging.info(f"write_off_points: {bonus.write_off_points}")
        total_earned += bonus.accrued_points if bonus.accrued_points else 0
        total_spent += bonus.write_off_points if bonus.write_off_points else 0
        #available_bonus += accrued_points if accrued_points else -write_off_points
        if len(soon_expiring) < 5 and bonus.expiration_date:
            #if isinstance(bonus.expiration_date, datetime.datetime):
            logging.info(f"soon_expiring: {len(soon_expiring)}")
            if bonus.expiration_date.date() > datetime.datetime.now().date():
                exp_date = bonus.expiration_date.strftime("%Y-%m-%d")
                soon_expiring.append(
                    {
                        "amount": bonus.accrued_points,
                        "expiresAt": exp_date,
                        "daysLeft": (bonus.expiration_date - datetime.datetime.now()).days
                    }
                )
        if bonus.expiration_date and bonus.expiration_date.date() <= datetime.datetime.now().date():
            expired_bonus += bonus.accrued_points
    if total_earned > 0:
        available_bonus += total_earned
    if total_spent > 0:
        available_bonus -= total_spent

    answer = {
        'clientId': client_b.id,
        'phoneNumber': client_b.phone_number,
        "availableBonus": available_bonus if available_bonus > 0 else 0,
        "pendingBonus": 0.0,
        "expiredBonus": expired_bonus,
        "totalEarned": total_earned,
        "totalSpent": total_spent,
        "soonExpiring": soon_expiring,
        "nextExpirationDate": soon_expiring[0].get('expiresAt') if soon_expiring else None
    }
    return answer


@router.get(
    "/api/v1/clients/bonus-history",
    tags=['client'],
    summary="Добавление отзыва клиента"
)
async def get_client_bonus_history(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone_number: str = Query(
            default=None,
            alias="phoneNumber",
            description="Телефонный номер пользователя",
            example="77077777777"
        ),
        client_id: int = Query(
            default=None,
            alias="clientId",
            description="Id клиента",
            example=123456
        ),
        limit: int = Query(
            default=20,
            alias="limit",
            description="Лимит",
            example=20
        ),
        offset: int = Query(
            default=0,
            alias="offset",
            description="Пропуск",
            example=0
        ),
        sort: Sort = Query(
            default=Sort.createdAt,
            alias="sort",
            description="Сортировка",
            example=Sort.createdAt
        ),
        order: Order = Query(
            default=Order.asc,
            alias="order",
            description="",
            example=Order.asc
        )
):
    session: AsyncSession = db_session.get()
    client_b = None
    if phone_number:
        client_b = await Client.get_client_by_phone(session=session, phone=phone_number)
    elif client_id:
        client_b = await session.get(Client, client_id)
    if not client_b:
        return HTTPException(status_code=204, detail="Client not found")
    logging.info(client_b.id)
    orders = {
        "asc": asc,
        "desc": desc
    }
    sorts = {
        "activationDate": ClientBonusPoints.activation_date,
        "expirationDate": ClientBonusPoints.expiration_date,
        "operationDate": ClientBonusPoints.operation_date,
        "createdAt": ClientBonusPoints.created_at
    }
    client_bonuses = await ClientBonusPoints.get_by_client_id(
        session=session,
        client_id=client_b.id,
        sort=sorts.get(sort.value),
        order=orders.get(order.value)
    )
    available_bonus = 0
    total_earned = 0
    total_spent = 0

    # client_bonuses = await ClientBonusPoints.get_by_client_id_limit(
    #     session=session,
    #     client_id=client_b.id,
    #     limit=20,
    #     offset=0
    # )
    logging.info(f"ClinetID -> {client_b.phone_number}")
    logging.info(f"Lens -> {len(client_bonuses)}")
    history = []
    for i, bonus in enumerate(client_bonuses):
        total_earned += bonus.accrued_points if bonus.accrued_points else 0
        total_spent += bonus.write_off_points if bonus.write_off_points else 0
        if i >= offset and len(history) < limit:
            purchase = await session.get(ClientPurchase, bonus.client_purchases_id)
            logging.info(bonus.client_purchases_id)
            if bonus.client_purchases_return_id:
                logging.info(bonus.client_purchases_return_id)
                purchase = await ClientPurchaseReturn.get_by_purchase_id(session, bonus.client_purchases_id)

            points = 0
            if bonus.accrued_points and bonus.accrued_points > 0:
                points = bonus.accrued_points
            if bonus.write_off_points and bonus.write_off_points > 0:
                points = bonus.write_off_points

            exp_date = None
            if bonus.expiration_date:
                exp_date = bonus.expiration_date.strftime("%Y-%m-%d")
            history.append(
                {
                    "source": bonus.source,
                    "siteId": purchase.site_id if purchase else None,
                    "mcId": purchase.mc_id if purchase else None,
                    "operationDate": bonus.operation_date,
                    "createdAt": bonus.created_at,
                    "type": "accrual" if bonus.accrued_points > 0 else "write_off",
                    "points": points,
                    "description": "",
                    "bonusExpirationDate": exp_date
                }
            )
    if total_earned > 0:
        available_bonus += total_earned
    if total_spent > 0:
        available_bonus -= total_spent
    answer = {
        "meta": {
            "total": len(client_bonuses),
            "limit": limit,
            "offset": offset
        },
        "data": {
            "clientId": client_b.id,
            "clientName": client_b.name,
            "balance": available_bonus if available_bonus > 0 else 0,
            "history": history
        }
    }

    return answer


@router.get("/api/v2/qr-code/generate-id",
            tags=['client'],
            summary="Генерация qr-code"
            )
async def get_generate_id(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str
):
    session: AsyncSession = db_session.get()
    client = await Client.get_client_by_phone(
        session=session,
        phone=parse_phone(phone)
    )
    code = await Cods.get_cody_by_phone(client.phone_number, session)
    if not code or (code and code.is_active) or (datetime.datetime.now() - code.created_at).total_seconds() / 60 > 15:
        code = await generate_code(session, phone_number=client.phone_number)

    return {
        "qrCode": code.code,
        "expiresAt": code.created_at + datetime.timedelta(minutes=15)
    }


@router.post("/client/reviews",
             tags=['client'],
             summary="Добавление отзыва клиента")
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


@router.post("/client/operator/notification",
             tags=['client'],
             summary="Отправка уведомлению по оценке работы оператора")
async def add_client_operator_grade(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str = Query(
            alias="phone",
            description="Телефонный номер пользователя",
            example="77077777777"
        ),
        telegram_id: typing.Optional[int] = Query(
            default=None,
            alias="phone",
            description="Телефонный номер пользователя",
            example="77077777777"
        )
):
    session: AsyncSession = db_session.get()
    bot = Bot(token=settings.tg_bot.bot_token, parse_mode='HTML')

    c = await Client.get_client_by_phone(session=session, phone=phone)
    app = await ClientsApp.get_last_app_by_phone(session=session, phone=c.phone_number)
    if app:
        if c.activity == 'telegram':
            await push_client_answer_operator(session=session, client_app=app, bot=bot, client=c)
        if c.activity == 'wb':
            # resp = requests.get(url=f"https://chatter.salebot.pro/api/a003aeed95f1655c1fe8b8b447570e19/whatsapp_callback?name=Test&message=grade&phone={phone}&bot_id=124652&txt={app.id}")
            wb = SendPlus(
                client_id=settings.wb_cred.client_id,
                client_secret=settings.wb_cred.client_secret,
                waba_bot_id=settings.wb_cred.wb_bot_id
            )
            await wb.send_template_by_phone(
                phone=phone,
                bot_id=settings.wb_cred.wb_bot_id,
                json=templates.get('operator')
            )
            app.is_push = True
            session.add(app)
            await session.commit()
        return {
            "status_code": status.HTTP_200_OK,
            "message": "Уведомление отправлено"
        }
    else:
        return {
            "status_code": status.HTTP_200_OK,
            "message": f"Пользователь с {phone} не найден в базе"
        }


@router.post("/client/mailing",
             tags=['client'],
             summary="Добавление клиента в рассылки")
async def client_mailing(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str = Query(
            alias="phone",
            description="Телефонный номер пользователя",
            example="77077777777"
        )
):
    session: AsyncSession = db_session.get()
    c = await Client.get_client_by_phone(session=session, phone=parse_phone(phone))
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


@router.post("/client/bitrix/lead",
             tags=['client'],
             summary="Создание лида в битрексе")
async def client_create_lead(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        operator: ModelLead
):
    session: AsyncSession = db_session.get()
    c = await Client.get_client_by_phone(session=session, phone=parse_phone(operator.phone))
    now_date = datetime.datetime.now()
    if operator.waiting_time == '':
        operator.waiting_time = 0
    date = now_date + datetime.timedelta(minutes=int(operator.waiting_time))
    texts = {
        'kaz': 'Таңдағаныңыз үшін рақмет! Оператор сізбен көрсетілген уақытта хабарласады.',
        'rus': 'Спасибо за выбор! Оператор свяжется с вами в указанное время.'
    }
    texts_cancel = {
        'kaz': 'Сіз өтініш жібердіңіз, оператор сұрауыңызға жауап бергенше күтіңіз',
        'rus': 'Вы уже подавали заявку, подождите пока оператор ответит на ваш запрос'
    }
    if c:
        if not (client_app := await ClientsApp.get_last_app_by_phone(
                session=session,
                phone=parse_phone(operator.phone)
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
                "id": resp.get('result'),
                "message": texts.get(operator.loc)
            }
        return {
            "status_code": status.HTTP_200_OK,
            "find": True,
            "create": False,
            'id': client_app.id,
            "message": texts_cancel.get(operator.loc)
        }
    return {
        "status_code": status.HTTP_200_OK,
        "find": False,
        "create": False,
        "message": f"Пользователь с {operator.phone} не найден в базе"
    }


@router.patch("/client/bitrix/lead",
              tags=['client'],
              summary="Добавление оценки оператора в лиде битрекса")
async def client_create_lead(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        operator: ModelLead
):
    session: AsyncSession = db_session.get()
    c = await Client.get_client_by_phone(session=session, phone=parse_phone(operator.phone))
    text = {
        'kaz': grade_text_kaz,
        'rus': grade_text
    }
    if c:
        client_app = await ClientsApp.get_last_app_by_phone(
            session=session,
            phone=parse_phone(operator.phone)
        )
        client_app.is_push = True
        session.add(client_app)
        await session.commit()
        await Leads(
            user_id=settings.bitrix.user_id,
            basic_token=settings.bitrix.token
        ).update(
            fields={
                "ID": client_app.id,
                "FIELDS[UF_CRM_1731932281238]": operator.grade
            }
        )
        return {
            "status_code": status.HTTP_200_OK,
            "find": True,
            "update": True,
            "message": text.get(operator.loc).get(operator.grade in ['1', '2', '3'])
        }

    return {
        "status_code": status.HTTP_200_OK,
        "find": False,
        "update": False,
        "message": f"Пользователь с {operator.phone} не найден в базе"
    }


@router.post("/client/validation_date",
             tags=['client'])
async def client_create(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        model_client: ModelAuthSite
):
    session: AsyncSession = db_session.get()
    answer = {
        "statusСode": 200,
        "message": "Клиент успешно обновлен"
    }
    if not model_client.phoneNumber:
        return {
            "statusСode": 400,
            "message": "Не заполнен телефон"
        }
    try:
        bot = Bot(token=settings.tg_bot.bot_token, parse_mode='HTML')
        if not (client := await Client.get_client_by_phone(
            session=session,
            phone=parse_phone(model_client.phoneNumber))
        ):
            client = Client()
            if not re.match(r'(?<!\d)\d{8,15}(?!\d)', parse_phone(model_client.phoneNumber)):
                return {
                    "statusСode": 400,
                    "message": "Не правильный формат номера"
                }
            client.phone_number = parse_phone(model_client.phoneNumber)
            client.source = model_client.source
            client.is_active = True
            answer["statusСode"] = 201
            answer["message"] = "Клиент успешно создан"
        answer["telegramId"] = client.id if await check_user_exists(client.id, bot) else None
        if model_client.clientFullName:
            #if not regex.fullmatch(r'^[\p{L}\s]+$', model_client.clientFullName):
                # return {
                #     "statusСode": 400,
                #     "message": "ФИО не должно содержать цифры и символы"
                # }
            client.name = model_client.clientFullName
        if model_client.birthDate:
            date = await parse_date(model_client.birthDate)
            if date is None:
                return {
                    "statusСode": 400,
                    "message": "Не правильный формат даты"
                }
            downgrade_date = datetime.datetime.strptime("01.01.1900", "%d.%m.%Y")
            if date.date() >= datetime.datetime.now().date():
                return {
                    "statusСode": 400,
                    "message": "Дата рождения не может быть позже текущей даты"
                }
            if date < downgrade_date:
                return {
                    "statusСode": 400,
                    "message": "Дата рождения не может быть раньше 01.01.1900"
                }
            client.birthday_date = date
        if model_client.gender:
            if model_client.gender != 'F' and model_client.gender != 'M':
                return {
                    "statusСode": 400,
                    "message": "Не правильно заполнен гендер"
                }
            client.gender = model_client.gender
        if model_client.email:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', model_client.email):
                return {
                    "statusСode": 400,
                    "message": "Не правильный email"
                }
            client.email = model_client.email
        else:
            return {
                "statusСode": 400,
                "message": "Не заполнен email"
            }
        session.add(client)
        await session.commit()
        return answer
    except HTTPException as ex:
        print(ex)
        return {
            "statusСode": 400,
            "message": "Некорректный формат данных"
        }


@router.get("/client/validation_date",
            tags=['client'])
async def client_create(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        birth: str = Query(
            alias="birthDate",
            description="Дата рождения",
            example="19.06.205"
        )
):
    try:
        if birth:
            b_date = await parse_date(birth)
            if not b_date:
                return {
                    "statusСode": 400,
                    "message": "Не правильный формат даты"
                }
            downgrade_date = datetime.datetime.strptime("01.01.1900", "%d.%m.%Y")
            if b_date.date() >= datetime.datetime.now().date():
                return {
                    "statusСode": 400,
                    "message": "Дата рождения не может быть позже текущей даты"
                }
            if b_date < downgrade_date:
                return {
                    "statusСode": 400,
                    "message": "Дата рождения не может быть раньше 01.01.1900"
                }
            client.birthday_date = b_date
            return {
                "statusСode": 200,
                "message": "Дата корректная"
            }

        return {
            "statusСode": 400,
            "message": "Ошибка"
        }
    except:
        return {
            "statusСode": 400,
            "message": "Ошибка"
        }


@router.post('/client/verification',
             tags=['client'],
             deprecated=True)
async def client_send_verification_code(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str,
        code: str
):
    verification_temp = {
        'kaz': {
            "name": "auth_code_kz",
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": code
                        }
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {
                            "type": "text",
                            "text": code
                        }
                    ]
                }
            ],
            "language": {
                "policy": "deterministic",
                "code": "kk"
            }
        },
        'rus': {
            "name": "auth_code_ru",
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": code
                        }
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [
                        {
                            "type": "text",
                            "text": code
                        }
                    ]
                }
            ],
            "language": {
                "policy": "deterministic",
                "code": "ru"
            }
        }
    }
    wb = SendPlus(
        client_id=settings.wb_cred.client_id,
        client_secret=settings.wb_cred.client_secret,
        waba_bot_id=settings.wb_cred.wb_bot_id
    )
    await wb.send_template_by_phone(
        phone=phone,
        bot_id=settings.wb_cred.wb_bot_id,
        json=verification_temp
    )
    return {
        'status_code': status.HTTP_200_OK,
        'message': 'Сообщение отправлено'
    }


@router.post('/client/quality_grade',
             tags=['client'],
             deprecated=True)
async def client_send_quality_grade(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone: str
):
    wb = SendPlus(
        client_id=settings.wb_cred.client_id,
        client_secret=settings.wb_cred.client_secret,
        waba_bot_id=settings.wb_cred.wb_bot_id
    )
    await wb.send_template_by_phone(
        phone=phone,
        bot_id=settings.wb_cred.wb_bot_id,
        json=templates.get('grade')
    )
    return {
        'status_code': status.HTTP_200_OK,
        'message': 'Сообщение отправлено'
    }


@router.post('/client/template',
             tags=['client'])
async def add_template_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        template: ModelTemplate
):
    session: AsyncSession = db_session.get()
    temp = MessageTemplate(
        channel=template.channel,
        even_type=template.event_type,
        audience_type=template.audience_type,
        title_template=template.title_template,
        body_template=template.body_template,
        local=template.local,
        is_active=True
    )
    session.add(temp)
    await session.commit()


@router.get('/client/get_credits',
            tags=['dev'])
async def add_template_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        date_in: str
):
    session: AsyncSession = db_session.get()
    results = await ClientBonusPoints.get_credited_bonuses(
        session,
        datetime.datetime.strptime(date_in, "%d.%m.%Y").date())
    logging.info(datetime.datetime.strptime(date_in, "%d.%m.%Y").date())
    answer = []
    bonuses = {}
    logging.info(len(results))
    for r in results:
        if not bonuses.get(r.client_purchases_id):
            bonuses[r.client_purchases_id] = {
                "client_id": r.client_id,
                "purchase_id": r.client_purchases_id,
                "accrued_points": r.accrued_points,
                "write_off_points": r.write_off_points,
                "expiration_date": r.expiration_date,
                "activation_date": r.activation_date
            }
            logging.info(r.client_purchases_id)
            res = await ClientBonusPoints.get_by_purchase_id(
                session=session,
                purchase_id=r.client_purchases_id,
                accrued_points=r.accrued_points
            )
            logging.info(len(res))
            if len(res) > 0:
                bonuses.pop(r.client_purchases_id)

    return bonuses


@router.get('/client/get_debits',
            tags=['dev'])
async def add_template_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        days: int
):
    session: AsyncSession = db_session.get()
    results = await ClientBonusPoints.get_debited_bonuses(
        session,
        days
    )

    answer = []
    for r in results:
        answer.append(
            {
                "client_id": r.client_id,
                "purchase_id": r.client_purchases_id,
                "accrued_points": r.accrued_points,
                "write_off_points": r.write_off_points,
                "expiration_date": r.expiration_date,
                "activation_date": r.activation_date
            })
    return answer
