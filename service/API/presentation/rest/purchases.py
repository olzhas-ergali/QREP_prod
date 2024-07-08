import typing

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse
from loguru import logger

from service.API.domain.authentication import security, validate_security
from service.API.infrastructure.database.commands import staff
from service.API.infrastructure.database.session import db_session
from service.API.infrastructure.models.purchases import ModelPurchase, ModelUser, ModelPurchaseReturn

router = APIRouter()


@router.get('/purchases/count')
async def get_count(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        user_id: int
):
    session = db_session.get()
    return await staff.get_purchases_count(session, user_id)


@router.post('/purchases')
async def add_purchases_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        purchase: ModelPurchase
):
    session: AsyncSession = db_session.get()
    return await staff.add_purchases(
        purchase_id=purchase.purchaseId,
        session=session,
        user_id=purchase.telegramId if purchase.telegramId != -1 else None,
        phone=purchase.phone,
        products=purchase.products
    )


@router.post('/purchases/return')
async def add_purchases_return_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        purchase: ModelPurchaseReturn
):
    session: AsyncSession = db_session.get()
    if purchase.returnId != '-1':
        return await staff.add_return_purchases(
            purchase_id=purchase.purchaseId,
            return_id=purchase.returnId,
            user_id=purchase.telegramId if purchase.telegramId != -1 else None,
            phone=purchase.phone,
            session=session,
            products=purchase.products,
        )
    else:
        return {
            "statusCode": status.HTTP_403_FORBIDDEN,
            "message": "Return id не может быть пустым",
        }


@router.post('/add_user')
async def add_user_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        user: ModelUser
):
    session: AsyncSession = db_session.get()
    return await staff.add_user_temp(
        session=session,
        name=user.name,
        user_id=user.telegramId,
        phone=user.phone
    )


@router.get('/get_user')
async def get_user_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        phone_number: str
):
    session: AsyncSession = db_session.get()
    user = await staff.get_user(
        session=session,
        phone=phone_number
    )
    return {"Name": user.name, "UserId": user.id}
