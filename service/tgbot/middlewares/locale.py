from typing import Tuple, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types

from service.tgbot.models.database.users import User, Client


class ACLMiddleware(I18nMiddleware):

    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        obj = args[0]

        pool = obj.bot.get('pool')
        session: AsyncSession = pool()
        user = await session.get(User, obj.from_user.id)
        if not user:
            user = await session.get(Client, obj.from_user.id)
        await session.close()
        return user.local or 'rus' if user else 'rus'
