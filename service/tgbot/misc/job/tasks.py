import typing
import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, extract, not_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload

from service.tgbot.models.database.users import RegTemp
from service.tgbot.keyboards.auth import get_continue_btn


async def push_client_authorization(
        pool: sessionmaker,
        bot: Bot,
):
    logging.info("pushing_client")
    session: AsyncSession = pool()
    now = datetime.now() - timedelta(minutes=3)
    response = await session.execute(select(RegTemp).where(
        (RegTemp.state_time < now))
    )
    users: typing.Optional[typing.List, None] = response.scalars().all()

    for u in users:
        try:
            await bot.send_message(
                chat_id=u.telegram_id,
                text="Вы не закончили регистрацию",
                reply_markup=get_continue_btn()
            )
        except:
            pass

    await session.close()
