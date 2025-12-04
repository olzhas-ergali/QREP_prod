from typing import Tuple, Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types
from sqlalchemy.orm import joinedload

from service.API.infrastructure.database.models import User, Client


class ACLMiddleware(I18nMiddleware):

    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        obj = args[0]

        pool = obj.bot.get('pool')
        session: AsyncSession = pool()
        
        # - OLD
        # user = await session.get(User, obj.from_user.id)
        # locale = "rus"
        # if user:
        #     locale = user.local
        
        # + NEW
        stmt = select(User).options(joinedload(User.profile)).where(User.id == obj.from_user.id)
        user = await session.scalar(stmt)
        
        locale = "rus"
        if user and user.profile and user.profile.local:
            locale = user.profile.local
            
        await session.close()
        return locale
