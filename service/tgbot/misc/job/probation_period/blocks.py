import asyncio

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from service.tgbot.keyboards.staff.probation_period import (
    get_input_question_for_probation_period_btn,
    get_evaluation_btn, get_action_btn, get_answer_question_btn
)
from service.tgbot.misc.states.staff import ProbationPeriodState
from service.tgbot.models.database.users import User


async def send_message_about_question(
        bot: Bot,
        user_id: int,
        text: str,
):
    await bot.send_message(
        chat_id=user_id,
        text=text
    )


async def notification_about_first_day(
        bot: Bot,
        user: User,
        storage: MemoryStorage,

):
    text = f"""
Привет, {user.fullname}. Я очень рад, что ты  часть нашей команды. Меня зовут Qrep, и я буду твоим помощником в период твоей адаптации.   Давай я поделюсь контактами коллег, к которым ты можешь обращаться в первые месяцы работы!                      
    """
    await bot.send_message(
        chat_id=user.id,
        text=text
    )

    text = """
Давай я тебе расскажу вкратце о правилах трудового распорядка в компании)
    """

    await bot.send_message(
        chat_id=user.id,
        text=text
    )

    await send_message_about_question(
        bot=bot,
        user_id=user.id,
        text="""
Подскажи, у тебя остались вопросы?
Если да, то напиши, пожалуйста. Мы свяжемся и ответим на них :)
        """,
    )

    await storage.set_state(
        chat=user.id,
        user=user.id,
        state=ProbationPeriodState.first_day.state
    )


async def notification_about_second_day(
        bot: Bot,
        user: User,
        **kwargs
):
    text = """
Привет! Как дела? Оцени свой первый день от 1 до 5
    """

    await bot.send_message(
        chat_id=user.id,
        text=text,
        reply_markup=get_evaluation_btn(
            current_day=2,
            action="work_evaluation"
        )
    )


async def notification_about_third_day(
        bot: Bot,
        user: User,
        **kwargs
):
    text = """
Привет! Вау, мы уже 3 дня вместе! Сегодня я хотел бы поговорить с тобой о культуре и коммуникации в компании.
    """

    await bot.send_message(
        chat_id=user.id,
        text=text
    )

    await asyncio.sleep(0.3)
    text = "Каналы связи:"

    await bot.send_message(
        chat_id=user.id,
        text=text
    )

    text = """
Ты уже есть во всех каналах(Bitrix24, Whatsapp, @qr.family?)
    """
    await bot.send_message(
        chat_id=user.id,
        text=text,
        reply_markup=get_action_btn(
            values=[
                "Да", "Нет"
            ],
            action='social',
            current_day=3
        )
    )


async def notification_about_fourth_day(
        bot: Bot,
        user: User,
        **kwargs
):
    text = """
Привет! Я про тебя не забыл :) Сегодня ты узнаешь что такое испытательный срок и какие преимущества есть в Qazaq Republic!
    """

    await bot.send_message(
        chat_id=user.id,
        text=text
    )
    await asyncio.sleep(0.3)

    text = """
Давай сперва расскажу про испытательный срок…
    """

    await bot.send_message(
        chat_id=user.id,
        text=text
    )

    await asyncio.sleep(0.3)

    text = """
Насколько была  полезной информация от 1 до 5?
    """

    await bot.send_message(
        chat_id=user.id,
        text=text,
        reply_markup=get_evaluation_btn(
            current_day=4,
            action='evaluation_information'
        )
    )


async def notification_about_five_day(
        bot: Bot,
        user: User,
        **kwargs
):
    text = """
Привет! Поздравляю, с успешной адаптационной неделей! 
Давай напоследок отвечу на часто задаваемые вопросы: 
    """

    await bot.send_message(
        chat_id=user.id,
        text=text,
    )

    await asyncio.sleep(0.3)

    await bot.send_message(
        chat_id=user.id,
        text="В каких числах я получу зарплату?",
        reply_markup=get_answer_question_btn(
            current_day=5,
            action='question',
            question_id=1
        )
    )
