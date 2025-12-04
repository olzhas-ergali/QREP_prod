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
from service.tgbot.models.database.users import User


async def notification_about_lessons(
        bot: Bot,
        pool: sessionmaker,
        storage: typing.Union[
            MemoryStorage,
            RedisStorage2
        ]
):
    """
    Уведомление об уроках

    """

    session: AsyncSession = pool()
    date_now = datetime.datetime.now()

    probation_period_days_next = PROBATION_PERIOD_DAYS + 1  # Мы задачу запускаем на следующий день, поэтому так

    # stmt = select(
    #     User
    # ).where(
    #     func.cast(User., Date) + datetime.timedelta(days=probation_period_days_next) >= date_now.date()
    # )
    stmt = select(
        User
    ).where(
        (date_now.date() > func.cast(User.date_receipt, Date)) &
        (func.cast(User.date_receipt, Date) + datetime.timedelta(days=30) >= date_now.date())
        )

    response = await session.execute(stmt)
    users: typing.List[User] = response.scalars().all()
    logging.info(users)
    notification_functions = {
        1: notification_about_first_day,
        2: notification_about_second_day,
        3: notification_about_third_day,
        4: notification_about_fourth_day,
        5: notification_about_five_day
    }
    await session.close()

    for user in users:
        # Получаем текущий день испытательного срока
        # end_date_probation_period = user.date_receipt.date() + datetime.timedelta(days=probation_period_days_next)
        # current_day_probation_period = probation_period_days_next - (end_date_probation_period - date_now.date()).days
        end_date_probation_period = user.created_at.date() + datetime.timedelta(days=probation_period_days_next)
        print(end_date_probation_period)
        current_day_probation_period = probation_period_days_next - (end_date_probation_period - date_now.date()).days
        print(current_day_probation_period)
        logging.info(f"IIN -> {user.iin}\n DAY -> {current_day_probation_period}")
        notification_function = notification_functions.get(current_day_probation_period)
        #print(current_day_probation_period)
        if notification_function is None:
            continue

        try:

            await notification_function(
                bot=bot,
                user=user,
                storage=storage
            )

        except Exception as e:
            logging.info(e)
        finally:
            await asyncio.sleep(0.2)
    await session.close()
