from aiogram import Bot
from aiogram.utils.exceptions import ChatNotFound


async def check_user_exists(
        user_id: int,
        bot: Bot
):
    try:
        user = await bot.get_chat(user_id)
        session = await bot.get_session()
        await session.close()
        return True
    except ChatNotFound:
        return False
