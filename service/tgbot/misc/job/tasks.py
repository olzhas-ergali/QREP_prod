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

from service.tgbot.models.database.users import RegTemp, ClientsApp
from service.tgbot.keyboards.auth import get_continue_btn
from service.tgbot.keyboards.client.faq import get_answer
from service.tgbot.models.database.loyalty import BonusExpirationNotifications, ClientBonusPoints


async def push_client_authorization(
        pool: sessionmaker,
        bot: Bot,
):
    logging.info("Уведомление для клиентов, которые не закончили регистрацию")
    session: AsyncSession = pool()
    now = datetime.now() - timedelta(minutes=3)
    response = await session.execute(select(RegTemp).where(
        (RegTemp.state_time < now) & (RegTemp.state != 'start'))
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


async def push_client_answer_operator(
        pool: sessionmaker,
        bot: Bot,
):
    logging.info("Уведомление для клиентов по оценке работе оператора")
    session: AsyncSession = pool()

    now = datetime.now()
    response = await session.execute(select(ClientsApp).where(
        (ClientsApp.waiting_time < now) & (ClientsApp.is_push == False))
    )
    users: typing.Optional[typing.List, None] = response.scalars().all()
    for u in users:
        try:
            await bot.send_message(
                chat_id=u.telegram_id,
                text="Ваш вопрос решен",
                reply_markup=get_answer()
            )
            u.is_push = True
            session.add(u)
        except:
            pass
    await session.commit()
    await session.close()


async def push_client_about_bonus(
        pool: sessionmaker,
        bot: Bot,
):
    logging.info("Уведомление для клиентов по сгоранию бонусов")
    session: AsyncSession = pool()
    date_now = datetime.now()
    bonuses = await ClientBonusPoints.get_bonuses(session)
    if bonuses:
        texts = {
            30: "Через 30 дней сгорят ваши бонусы. Используйте их, пока не поздно.",
            7: "Вы можете потратить бонусы до истечения срока действия. Осталось 7 дней.",
            1: "Завтра ваши бонусы станут недоступны. Успейте их использовать сегодня!"
        }
        for bonus in bonuses:
            await bot.send_message(
                chat_id=bonus.client_id,
                text=texts.get((date_now - bonus.expiration_date).days)
            )
    await session.close()

