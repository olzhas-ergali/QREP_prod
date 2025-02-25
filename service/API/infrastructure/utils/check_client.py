from aiogram import Bot
from aiogram.utils.exceptions import ChatNotFound


async def check_user_exists(
        user_id: int,
        bot: Bot
):
    try:
        user = await bot.get_chat(user_id)
        await bot.close()
        return True
    except ChatNotFound:
        return False
