import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.engine import URL

from service.tgbot.misc.job.probation_period import notification_about_lessons
from service.tgbot.data import I18N_DOMAIN, LOCALES_DIR
from service.tgbot.models.database.base import Database
from service.tgbot.config import load_config
from service.tgbot.filters.auth import AuthFilter
from service.tgbot.filters.admin import AdminFilter
from service.tgbot.filters.client_auth import ClientAuthFilter
from service.tgbot.filters.i18n import I18nTextFilter
from service.tgbot.middlewares.db import DbMiddleware
from service.tgbot.middlewares.locale import ACLMiddleware
from service.tgbot.misc.job import tasks, probation_period
from service.tgbot.misc.job.staff import tasks as staff_task
from service.tgbot import handlers

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR, 'rus')
    dp.setup_middleware(DbMiddleware())
    dp.setup_middleware(i18n)
    return i18n


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(AuthFilter)
    dp.filters_factory.bind(ClientAuthFilter)
    dp.filters_factory.bind(I18nTextFilter)


def register_all_handlers(dp):
    handlers.register.register_staff(dp)
    handlers.staff.register.register_staff_function(dp)
    handlers.client.register.register_client_function(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',

    )
    logger.info("Starting bot")
    config = load_config(".env")
    if config.tg_bot.use_redis:
        storage = RedisStorage2(config.tg_bot.redis_host)
    else:
        storage = MemoryStorage()

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    db = Database()

    scheduler = AsyncIOScheduler(
        timezone='Asia/Aqtobe'
    )
    await db.create_pool(
        URL(
            drivername="postgresql+asyncpg",
            username=config.db.user,
            password=config.db.password,
            host=config.db.host,
            database=config.db.database,
            query={},
            port=5432
        )
    )

    dp = Dispatcher(bot, storage=storage)
    # redis = await storage.redis()

    i18n = register_all_middlewares(dp)
    bot['i18n'] = i18n.gettext

    bot['config'] = config
    bot['pool'] = db.pool

    scheduler.add_job(
        tasks.push_client_authorization,
        'cron',
        hour=15,
        minute=00,
        args=(db.pool, bot)
    )

    scheduler.add_job(
        probation_period.notification_about_lessons,
        'cron',
        hour=9,
        minute=00,
        args=(bot, db.pool, storage),

    )
    scheduler.add_job(
        staff_task.push_staff_about_dismissal,
        'cron',
        hour=10,
        minute=00,
        args=(bot, db.pool,),
    )

    # scheduler.add_job(
    #     tasks.push_client_about_bonus,
    #     'cron',
    #     hour=10,
    #     minute=00,
    #     args=(db.pool, bot),
    #
    # )
    # scheduler.add_job(
    #     tasks.push_client_about_bonus,
    #     'interval',
    #     minutes=1,
    #     args=(db.pool, bot),
    # )
    # scheduler.add_job(
    #     staff_task.push_staff_about_dismissal,
    #     'cron',
    #     hour=10,
    #     minute=00,
    #     args=(db.pool, bot)
    # )
    # bot['redis'] = redis

    # register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    bot_me = await bot.me
    logging.info(
        f'starting bot: @{bot_me.username}'
    )

    # start
    try:
        # arr = ['371683935', '398864433', '412249576',
        #       '428917660', '483200140', '564023521',
        #       '875863049', '1006269986', '5551195067',
        #       '6845418199']
        # for i in arr:
        #    try:
        #        await bot.send_message(i, "Функционал бота обновлен, нажмите /start")
        #    except:
        #        pass
        scheduler.start()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
