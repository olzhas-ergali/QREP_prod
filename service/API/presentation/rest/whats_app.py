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


#@router.get()
