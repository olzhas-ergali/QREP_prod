import asyncio
import datetime
import logging
import typing

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from service.tgbot.data.helpers import PROBATION_PERIOD_DAYS
from service.tgbot.misc.job.probation_period.blocks import notification_about_first_day, notification_about_second_day, \
    notification_about_third_day, notification_about_fourth_day, notification_about_five_day
from service.tgbot.models.database.users import User



async def notification_about_lessons(
        bot: Bot,
        pool: sessionmaker
):
    """
    Уведомление об уроках

    """


    session: AsyncSession = pool()
    date_now = datetime.datetime.now()
    end_date_probation_period = date_now + datetime.timedelta(days=PROBATION_PERIOD_DAYS)
    stmt = select(
        User
    ).where(
        User.date_receipt >= end_date_probation_period
    )
    response = await session.execute(stmt)
    users: typing.List[User] = response.scalars().all()


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
        current_day_probation_period = PROBATION_PERIOD_DAYS - (end_date_probation_period - date_now).days

        try:
            notification_function = notification_functions.get(current_day_probation_period)

            await notification_function(bot, user)

        except Exception as e:
            logging.exception(e)
        finally:
            await asyncio.sleep(0.2)


