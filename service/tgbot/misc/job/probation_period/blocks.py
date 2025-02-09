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
    _ = bot.get('i18n')
    reply_markup = get_action_btn(
        values=[
            _("Да", locale=user.local), _("Нет", locale=user.local)
        ],
        action='first',
        current_day=1
    )
    text = _("Привет, {name}. Я очень рад, что ты стал(а) частью нашей команды. Меня зовут Qrep, и я буду твоим помощником в период твоей адаптации. Для начала расскажу немного о нас. Наша компания стремится к улучшению жизни общества, создавая качественные продукты на каждый день, дополняя образ современного человека. А ты знаешь историю появления нашего бренда?",
             locale=user.local).format(name=user.name)

    await bot.send_message(
        chat_id=user.id,
        text=text,
        reply_markup=reply_markup
    )

# async def notification_about_first_day(
#         bot: Bot,
#         user: User,
#         storage: MemoryStorage,
#         i18n_func
# ):
    # _ = bot.get('i18n')
    #media = MediaGroup()
    # videos = {
    #     'kaz': FILES_DIRECTORY / "DianaKaz.mp4",
    #     'rus': FILES_DIRECTORY / "DianaRus.mp4"
    # }
    # files = {
    #     'kaz': FILES_DIRECTORY / "Фото с контактами на каз.pdf",
    #     'rus': FILES_DIRECTORY / "Фото с контактами на русс.pdf"
    # }
    # media.attach_video(InputMediaVideo(media=open(videos.get(user.local), "rb")))
    #media.attach_video(InputMediaVideo(media=open(videos.get('rus'), "rb")), caption="На русском")
    #Сәлем, {user.fullname}. Сен біздің команданың бір бөлігі болғаныңа өте қуаныштымын. Менің атым Qrep, мен сенің бейімделу кезеңінде көмекшің боламын.   Жұмыстың алғашқы айларында хабарласуға болатын әріптестеріміздің нөмірімен бөлісемін!\n
    # await bot.send_document(
    #     chat_id=user.id,
    #     caption=text,
    #     document=InputFile(files.get(user.local), files.get(user.local).name)
    # )
    # await bot.send_document(
    #     chat_id=user.id,
    #     caption=texts.get('rus'),
    #     document=InputFile(files.get('rus'), files.get('rus').name)
    # )
    # reply_markup = get_action_btn(
    #     values=[
    #         _("Да"), _("Нет")
    #     ],
    #     action='first',
    #     current_day=1
    # )
    # text = _("Привет, {name}. Я очень рад, что ты стал(а) частью нашей команды. Меня зовут Qrep, и я буду твоим помощником в период твоей адаптации. Для начала расскажу немного о нас. Наша компания стремится к улучшению жизни общества, создавая качественные продукты на каждый день, дополняя образ современного человека. А ты знаешь историю появления нашего бренда?").format(user.fullname)
    #
    # await bot.send_message(
    #     chat_id=user.id,
    #     text=text,
    #     reply_markup=reply_markup
    # )
    #Мен саған компаниядағы еңбек тәртібінің ережелері туралы қысқаша айтып берейін:)
    # text = _("Давай я тебе расскажу вкратце о правилах трудового распорядка в компании)")
    #
    # await bot.send_message(
    #     chat_id=user.id,
    #     text=text
    # )
    #
    # await bot.send_media_group(
    #     chat_id=user.id,
    #     media=media
    # )
    #Сенде сұрақтар қалды ма?
    #Егер сұрақтар қалса, жазып жібере аласын. Біз хабарласып, сұрақтарына жауап береміз:)\n
    # await send_message_about_question(
    #     bot=bot,
    #     user_id=user.id,
    #     text=_("Подскажи, у тебя остались вопросы?\nЕсли да, то напиши, пожалуйста. Мы свяжемся и ответим на них :)"),
    # )
    #
    # await storage.set_state(
    #     chat=user.id,
    #     user=user.id,
    #     state=ProbationPeriodState.first_day.state
    # )


async def notification_about_second_day(
        bot: Bot,
        user: User,
        **kwargs
):
    _ = bot.get('i18n')
    #Сәлем әріптес! Қалайсын? Бірінші жұмыс күніңді 1 ден 5 ке дейін бағала:\n
    text = _("Привет! Как дела? Оцени свой первый день от 1 до 5", locale=user.local)

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
    _ = bot.get('i18n')
    media = MediaGroup()
    videos = {
        'kaz': FILES_DIRECTORY / "SavicKaz.mp4",
        'rus': FILES_DIRECTORY / "SavicRus.mp4"
    }
    media.attach_video(InputMediaVideo(media=open(videos.get(user.local), "rb")))
    text = _('Привет! Вау, мы уже 3 дня вместе! Сегодня я хотел бы поговорить с тобой о культуре и коммуникации в компании. Мы используем несколько каналов для связи в компании. Чтобы быть в курсе всех новостей и быстрее решать вопросы, нужно подключиться ко всем каналам.',
             locale=user.local)

    await bot.send_message(
        chat_id=user.id,
        text=text
    )

    await asyncio.sleep(0.3)

    await bot.send_media_group(
        chat_id=user.id,
        media=media
    )
    #Сен қазірдің өзінде барлық арналарда барсың ба(Bitrix24, WhatsApp, @qr.family)?
    text = _("Ты уже есть во всех каналах(Bitrix24, Whatsapp, @qr.family?)",
             locale=user.local)
    await bot.send_message(
        chat_id=user.id,
        text=text,
        reply_markup=get_action_btn(
            values=[
                _("Да", locale=user.local), _("Нет", locale=user.local)
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
    _ = bot.get('i18n')
    #Сәлем! Мен сені ұмытқан жоқпын :) Бүгін сен Qazaq Republic компаниясындағы артықшылықтармен танысасың!
    text = _('Привет! Я про тебя не забыл :) Сегодня расскажу, что помимо работы, мы также ценим хороший отдых. Мы часто проводим тимбилдинги с командой и, кроме того, у нас есть крутой проект — QR Ambassadors для ребят из разных регионов!',
             locale=user.local)

    await bot.send_video(
        caption=text,
        video=InputFile(FILES_DIRECTORY / "Ambassador.mp4", (FILES_DIRECTORY / "Ambassador.mp4").name),
        chat_id=user.id
    )
    await asyncio.sleep(1)

    text = _('Наш проект направлен на улучшение взаимодействия и сотрудничества между регионами и сотрудниками через наших амбассадоров. Мы уверены, что ты также сможешь привнести свои новые идеи и установить прочные связи с коллегами!',
             locale=user.local)
    await bot.send_message(
        chat_id=user.id,
        text=text
    )

    text = _("Надеюсь информация была полезной! До скорой встречи!!",
             locale=user.local)
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
    _ = bot.get('i18n')
    text = _("Привет! Поздравляю, ты успешно прошел адаптационную неделю! Я рада была поделиться с тобой всей информацией, которой владею :)  И хочу пригласить тебя на Welcome Training!",
             locale=user.local)

    await bot.send_message(
        chat_id=user.id,
        text=text,
    )

    await asyncio.sleep(0.3)
    #"Саған оны қалай өткен ыңғайлырақ болады?\"
    await bot.send_message(
        chat_id=user.id,
        text=_("Как тебе будет удобнее пройти его?",
               locale=user.local),
        reply_markup=get_questions_btn(
            current_day=5,
            action='question',
            question_id=[1, 2],
            texts=['Онлайн', 'Оффлайн']
        )
    )
