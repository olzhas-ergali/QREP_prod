import logging
import typing

from aiogram import Bot
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse

from service.API.infrastructure.database.models import Revenue
from service.API.domain.authentication import security, validate_security
from service.API.infrastructure.models.revenue import RevenueDateModel
from service.API.infrastructure.database.commands.revenue import add_revenue_date
from service.API.infrastructure.database.session import db_session

router = APIRouter()


@router.post("/v1/revenue-data")
async def post_revenue_date_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        revenue: RevenueDateModel
):
    session = db_session.get()
    logging.info(revenue.json())
    return await add_revenue_date(
        session=session,
        revenue=revenue
    )


@router.put("/v1/revenue-data")
async def put_revenue_date_process(
        credentials: typing.Annotated[HTTPBasicCredentials, Depends(validate_security)],
        documentId: str,
        rowId: str,
        revenue: RevenueDateModel
):
    session = db_session.get()

    return await add_revenue_date(
        session=session,
        revenue=revenue,
        document_id=documentId,
        row_id=rowId
    )
