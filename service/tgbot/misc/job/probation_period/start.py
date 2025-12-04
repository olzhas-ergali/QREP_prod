import asyncio
import datetime
import logging
import typing

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage, RedisStorage2
from sqlalchemy import select, func, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from service.tgbot.data.helpers import PROBATION_PERIOD_DAYS
from service.tgbot.misc.job.probation_period.blocks import notification_about_first_day, notification_about_second_day, \
    notification_about_third_day, notification_about_fourth_day, notification_about_five_day
from sqlalchemy.orm import selectinload
from service.API.infrastructure.database.models import User, UserProfile


async def notification_about_lessons(
        bot: Bot,
        pool: sessionmaker,
        storage: typing.Union[MemoryStorage, RedisStorage2]
):
    session: AsyncSession = pool()
    date_now = datetime.datetime.now()
    probation_period_days_next = PROBATION_PERIOD_DAYS + 1

    stmt = select(User).options(
        selectinload(User.profile)
    ).join(UserProfile).where(
        (date_now.date() > func.cast(UserProfile.date_receipt, Date)) &
        (func.cast(UserProfile.date_receipt, Date) + datetime.timedelta(days=30) >= date_now.date())
    )
    response = await session.execute(stmt)
    users: typing.List[User] = response.scalars().all()
    
    notification_functions = {1: notification_about_first_day, 2: notification_about_second_day, 3: notification_about_third_day, 4: notification_about_fourth_day, 5: notification_about_five_day}
    
    for user in users:
        if not user.profile or not user.profile.date_receipt:
            continue
            
        days_since_receipt = (date_now.date() - user.profile.date_receipt.date()).days
        current_day_probation_period = days_since_receipt + 1

        notification_function = notification_functions.get(current_day_probation_period)
        if not notification_function:
            continue

        try:
            await notification_function(bot=bot, user=user, storage=storage)
        except Exception as e:
            logging.error(f"Failed to send probation notification to user {user.id}: {e}")
        finally:
            await asyncio.sleep(0.2)
    await session.close()