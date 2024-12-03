from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types import Poll, PollAnswer, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from service.tgbot.models.database.users import User, Client, RegTemp


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    async def pre_process(self, obj, data, *args):
        pool = obj.bot.get('pool')
        session: AsyncSession = pool()
        reg = await session.get(RegTemp, obj.from_user.id)
        staff = await session.get(User, obj.from_user.id)
        client = await session.get(Client, obj.from_user.id)
        if not isinstance(obj, (Message, CallbackQuery)):
            data['session'] = session
            return
        if not staff and not client:
            client = Client(
                id=obj.from_user.id,
                fullname=obj.from_user.full_name
            )
            session.add(client)

        if (not staff or not staff.iin) and not reg and not client.phone_number:
            reg = RegTemp()
            reg.telegram_id = obj.from_user.id
            reg.state = "start"
            session.add(reg)
        await session.commit()
            # staff = User(
            #    id=obj.from_user.id,
            #    fullname=obj.from_user.full_name
            # )
            # session.add(staff)
            # await session.commit()

        data['session'] = session
        data['reg'] = reg
        if staff and staff.iin:
            data['user'] = staff
        else:
            client.activity = "telegram"
            data['user'] = client

    async def post_process(self, obj, data, *args):
        if session := data.get("session"):
            await session.close()
            data.pop('session')
