from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types import Poll, PollAnswer, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from service.tgbot.models.database.users import User, Client


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    async def pre_process(self, obj, data, *args):
        pool = obj.bot.get('pool')
        session: AsyncSession = pool()

        if not isinstance(obj, (Message, CallbackQuery)):
            data['session'] = session
            return

        if not (user := await session.get(User, obj.from_user.id)) and not (
                client := await session.get(Client, obj.from_user.id)):
            client = Client(
                id=obj.from_user.id,
                fullname=obj.from_user.full_name
            )
            session.add(client)
            await session.commit()
            # staff = User(
            #    id=obj.from_user.id,
            #    fullname=obj.from_user.full_name
            # )
            # session.add(staff)
            # await session.commit()
        # if not

        data['session'] = session
        if user:
            data['user'] = user
        else:
            client.activity = "telegram"
            data['user'] = client

    async def post_process(self, obj, data, *args):
        if session := data.get("session"):
            await session.close()
            data.pop('session')
