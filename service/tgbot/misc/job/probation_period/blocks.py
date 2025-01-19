import asyncio

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputFile, MediaGroup, InputMediaVideo

from service.tgbot.keyboards.staff.probation_period import (
    get_input_question_for_probation_period_btn,
    get_evaluation_btn, get_action_btn, get_answer_question_btn, get_questions_btn
)
from service.tgbot.data.helpers import FILES_DIRECTORY
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
    media = MediaGroup()
    videos = {
        'kaz': FILES_DIRECTORY / "DianaKaz.mp4",
        'rus': FILES_DIRECTORY / "DianaRus.mp4"
    }
    files = {
        'kaz': FILES_DIRECTORY / "Фото с контактами на каз.pdf",
        'rus': FILES_DIRECTORY / "Фото с контактами на русс.pdf"
    }
    media.attach_video(InputMediaVideo(media=open(videos.get('kaz'), "rb")), caption="Қазақша")
    media.attach_video(InputMediaVideo(media=open(videos.get('rus'), "rb")), caption="На русском")
    texts = {
        'kaz': f"""
Сәлем, {user.fullname}. Сен біздің команданың бір бөлігі болғаныңа өте қуаныштымын. Менің атым Qrep, мен сенің бейімделу кезеңінде көмекшің боламын.   Жұмыстың алғашқы айларында хабарласуға болатын әріптестеріміздің нөмірімен бөлісемін!\n
""",
        'rus': f"""
Привет, {user.fullname}. Я очень рад, что ты  часть нашей команды. Меня зовут Qrep, и я буду твоим помощником в период твоей адаптации. Давай я поделюсь контактами коллег, к которым ты можешь обращаться в первые месяцы работы!\n
    """}

    await bot.send_document(
        chat_id=user.id,
        caption=texts.get('kaz'),
        document=InputFile(files.get('kaz'), files.get('kaz').name)
    )
    await bot.send_document(
        chat_id=user.id,
        caption=texts.get('rus'),
        document=InputFile(files.get('rus'), files.get('rus').name)
    )
    text = """
Мен саған компаниядағы еңбек тәртібінің ережелері туралы қысқаша айтып берейін:)\n
Давай я тебе расскажу вкратце о правилах трудового распорядка в компании)
    """

    await bot.send_message(
        chat_id=user.id,
        text=text
    )

    await bot.send_media_group(
        chat_id=user.id,
        media=media
    )
    await send_message_about_question(
        bot=bot,
        user_id=user.id,
        text="""
Сенде сұрақтар қалды ма?                                     
Егер сұрақтар қалса, жазып жібере аласын. Біз хабарласып, сұрақтарына жауап береміз:)\n
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
Сәлем әріптес! Қалайсын? Бірінші жұмыс күніңді 1 ден 5 ке дейін бағала:\n
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
    media = MediaGroup()
    videos = {
        'kaz': FILES_DIRECTORY / "SavicKaz.mp4",
        'rus': FILES_DIRECTORY / "SavicRus.mp4"
    }
    media.attach_video(InputMediaVideo(media=open(videos.get('kaz'), "rb")), caption="Қазақша")
    media.attach_video(InputMediaVideo(media=open(videos.get('rus'), "rb")), caption="На русском")
    text = """
Привет! Вау, мы уже 3 дня вместе! Сегодня я хотел бы поговорить с тобой о культуре и коммуникации в компании.\n
Сәлем! Уау, біз бірге жүргенімізге 3 күн болды! Бүгін мен саған компанияның мәдениеті мен коммуникациясы туралы айтып бергім келеді.
    """

    await bot.send_message(
        chat_id=user.id,
        text=text
    )

    await asyncio.sleep(0.3)

    await bot.send_media_group(
        chat_id=user.id,
        media=media
    )
    text = """
Ты уже есть во всех каналах(Bitrix24, Whatsapp, @qr.family?)
Сен қазірдің өзінде барлық арналарда барсың ба(Bitrix24, WhatsApp, @qr.family)?
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
    files = {
        'kaz': FILES_DIRECTORY / "ПРЕИМУЩЕСТВА на каз.pdf",
        'rus': FILES_DIRECTORY / "ПРЕИМУЩЕСТВА на русс.pdf"
    }
    texts = {
        'kaz': f"""
Біздің компанияда жұмыс істеудің қандай артықшылықтары бар:
    """,
        'rus': f"""
Какие есть преимущества работы в компании:
        """}
    text = """
Привет! Я про тебя не забыл :) Сегодня ты узнаешь что такое испытательный срок и какие преимущества есть в Qazaq Republic!
Сәлем! Мен сені ұмытқан жоқпын :) Бүгін сен Qazaq Republic компаниясындағы артықшылықтармен танысасың!
    """

    await bot.send_message(
        chat_id=user.id,
        text=text
    )
    await asyncio.sleep(1)

    await bot.send_document(
        chat_id=user.id,
        caption=texts.get('kaz'),
        document=InputFile(files.get('kaz'), files.get('kaz').name)
    )
    await bot.send_document(
        chat_id=user.id,
        caption=texts.get('rus'),
        document=InputFile(files.get('rus'), files.get('rus').name)
    )
    text = """
Ақпараттар пайдалы болды деп үміттенемін. Келесі кездескенше!!\n
Надеюсь информация была полезной! До скорой встречи!!
    """
    await asyncio.sleep(0.3)

    await bot.send_message(
        chat_id=user.id,
        text=text
    )


async def notification_about_five_day(
        bot: Bot,
        user: User,
        **kwargs
):
    text = """
Сәлем! Сен бейімделу аптасын сәтті өтуіңмен құттықтаймын! 
Мен саған бар білген ақпаратты бөліскеніме қуаныштымын :)\n
Енді сені Welcome Training-ге шақырғым келеді!
Привет! Поздравляю, ты успешно прошел адаптационную неделю! Я был рад поделиться с 
тобой всей информацией, которой владею :) И хочу пригласить тебя на Welcome Training!
    """

    await bot.send_message(
        chat_id=user.id,
        text=text,
    )

    await asyncio.sleep(0.3)

    await bot.send_message(
        chat_id=user.id,
        text="Саған оны қалай өткен ыңғайлырақ болады?\n\n"
             "Как тебе будет удобнее пройти его?",
        reply_markup=get_questions_btn(
            current_day=5,
            action='question',
            question_id=[1, 1],
            texts=['Онлайн', 'Оффлайн']
        )
    )
