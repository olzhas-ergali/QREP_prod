from aiogram.types.message import Message


async def remove(
        message: Message,
        step: int
):
    try:
        await message.bot.delete_message(message.from_user.id, message.message_id - step)
    except:
        pass