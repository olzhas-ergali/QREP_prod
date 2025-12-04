# service/tgbot/handlers/staff/onboarding_form/main.py

from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.dispatcher import FSMContext
from service.tgbot.misc.states.staff import OnboardingFormState
from service.API.infrastructure.database.models import User
from service.tgbot.keyboards.client.client import get_genders_ikb # Используем клавиатуру для пола

# ID HR-менеджера или группы, куда будут приходить результаты
HR_CHAT_ID = -1001234567890  # ЗАМЕНИТЕ НА РЕАЛЬНЫЙ ID чата HR

async def start_onboarding_form(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await message.answer(_("С радостью приветствую Вас в нашей компании! От имени всего коллектива желаю успехов и благополучия. Мы приступаем к onboarding в нашей команде."))
    
    # Безопасное получение локали
    locale = user.profile.local if user.profile else "rus"
    await message.answer(_("Ваше ФИО(как в удостоверении личности):"))
    await OnboardingFormState.waiting_fio_latin.set()

async def process_fio_latin(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(fio_latin=message.text)
    await message.answer(_("Дата рождения (дд.мм.гггг):"))
    await OnboardingFormState.waiting_dob.set()

async def process_dob(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(dob=message.text)
    await message.answer(_("Ваш пол:"), reply_markup=await get_genders_ikb(_))
    await OnboardingFormState.waiting_gender.set()
    
async def process_gender(query: CallbackQuery, state: FSMContext, callback_data: dict, user: User):
    _ = query.bot.get("i18n")
    gender = "Мужской" if callback_data.get('gender') == 'M' else "Женский"
    await state.update_data(gender=gender)
    await query.message.delete() # Удаляем кнопки
    await query.message.answer(_("Номер Вашего телефона:"))
    await OnboardingFormState.waiting_phone_number.set()

async def process_phone_number(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(phone_number=message.text)
    await message.answer(_("Фактический адрес проживания:"))
    await OnboardingFormState.waiting_address_fact.set()

async def process_address_fact(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(address_fact=message.text)
    await message.answer(_("Семейное положение:"))
    await OnboardingFormState.waiting_family_status.set()

async def process_family_status(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(family_status=message.text)
    await message.answer(_("Информация о детях (если есть):"))
    await OnboardingFormState.waiting_children_info.set()

async def process_children_info(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(children_info=message.text)
    await message.answer(_("Являетесь ли вы студентом? (Да/Нет)"))
    await OnboardingFormState.waiting_is_student.set()

async def process_is_student(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(is_student=message.text)
    await message.answer(_("Место рождения:"))
    await OnboardingFormState.waiting_birth_place.set()

# Дополнительные личные данные из Excel
async def process_birth_place(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(birth_place=message.text)
    await message.answer(_("Гражданство:"))
    await OnboardingFormState.waiting_citizenship.set()

async def process_citizenship(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(citizenship=message.text)
    await message.answer(_("Уровень образования:"))
    await OnboardingFormState.waiting_education_level.set()

async def process_education_level(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(education_level=message.text)
    await message.answer(_("Знание языков:"))
    await OnboardingFormState.waiting_languages.set()

async def process_languages(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(languages=message.text)
    await message.answer(_("Есть ли водительские права? (Да/Нет)"))
    await OnboardingFormState.waiting_driver_license.set()

async def process_driver_license(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(driver_license=message.text)
    await message.answer(_("Есть ли судимость? (Да/Нет)"))
    await OnboardingFormState.waiting_criminal_record.set()

async def process_criminal_record(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(criminal_record=message.text)
    await message.answer(_("Есть ли проблемы со здоровьем?"))
    await OnboardingFormState.waiting_health_issues.set()

async def process_health_issues(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(health_issues=message.text)
    await message.answer(_("Есть ли аллергии?"))
    await OnboardingFormState.waiting_allergies.set()

async def process_allergies(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(allergies=message.text)
    await message.answer(_("Принимаете ли постоянно лекарства?"))
    await OnboardingFormState.waiting_medications.set()

async def process_medications(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(medications=message.text)
    await message.answer(_("Курите ли? (Да/Нет)"))
    await OnboardingFormState.waiting_smoking.set()

async def process_smoking(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(smoking=message.text)
    await message.answer(_("Употребляете ли алкоголь?"))
    await OnboardingFormState.waiting_alcohol.set()

async def process_alcohol(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(alcohol=message.text)
    await message.answer(_("Ваши ожидания от первого дня работы:"))
    await OnboardingFormState.waiting_first_day_expectations.set()

async def process_first_day_expectations(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(first_day_expectations=message.text)
    await message.answer(_("Ваши ожидания от работы в целом:"))
    await OnboardingFormState.waiting_work_expectations.set()

async def process_work_expectations(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(work_expectations=message.text)
    await message.answer(_("Каковы ваши карьерные цели?"))
    await OnboardingFormState.waiting_career_goals.set()

# Дополнительные рабочие вопросы из Excel
async def process_career_goals(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(career_goals=message.text)
    await message.answer(_("Расскажите о предыдущем месте работы:"))
    await OnboardingFormState.waiting_previous_work.set()

async def process_previous_work(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(previous_work=message.text)
    await message.answer(_("Почему уволились с предыдущего места работы?"))
    await OnboardingFormState.waiting_why_quit_previous.set()

async def process_why_quit_previous(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(why_quit_previous=message.text)
    await message.answer(_("Какой график работы вам предпочтителен?"))
    await OnboardingFormState.waiting_work_schedule.set()

async def process_work_schedule(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(work_schedule=message.text)
    await message.answer(_("Каковы ваши зарплатные ожидания?"))
    await OnboardingFormState.waiting_salary_expectations.set()

async def process_salary_expectations(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(salary_expectations=message.text)
    await message.answer(_("Что вас мотивирует в работе?"))
    await OnboardingFormState.waiting_what_motivates.set()

async def process_what_motivates(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(what_motivates=message.text)
    await message.answer(_("Назовите ваши сильные стороны:"))
    await OnboardingFormState.waiting_strengths.set()

async def process_strengths(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(strengths=message.text)
    await message.answer(_("Назовите ваши слабые стороны:"))
    await OnboardingFormState.waiting_weaknesses.set()

async def process_weaknesses(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(weaknesses=message.text)
    await message.answer(_("Как вы справляетесь со стрессом?"))
    await OnboardingFormState.waiting_stress_management.set()

async def process_stress_management(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(stress_management=message.text)
    await message.answer(_("Как вы решаете конфликты?"))
    await OnboardingFormState.waiting_conflict_resolution.set()

async def process_conflict_resolution(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(conflict_resolution=message.text)
    await message.answer(_("Ваши хобби и интересы:"))
    await OnboardingFormState.waiting_hobby.set()

async def process_hobby(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(hobby=message.text)
    await message.answer(_("Контакты для экстренной связи:"))
    await OnboardingFormState.waiting_emergency_contact.set()

async def process_emergency_contact(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(emergency_contact=message.text)
    await message.answer(_("Ваш Instagram (если есть):"))
    await OnboardingFormState.waiting_instagram.set()

async def process_instagram(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(instagram=message.text)
    await message.answer(_("Любимая музыка:"))
    await OnboardingFormState.waiting_favorite_music.set()

async def process_favorite_music(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(favorite_music=message.text)
    await message.answer(_("Любимые фильмы:"))
    await OnboardingFormState.waiting_favorite_movies.set()

# Дополнительные личные интересы из Excel
async def process_favorite_movies(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(favorite_movies=message.text)
    await message.answer(_("Любимые книги:"))
    await OnboardingFormState.waiting_favorite_books.set()

async def process_favorite_books(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(favorite_books=message.text)
    await message.answer(_("Занимаетесь ли спортом?"))
    await OnboardingFormState.waiting_sports.set()

async def process_sports(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(sports=message.text)
    await message.answer(_("Опыт путешествий (куда ездили):"))
    await OnboardingFormState.waiting_travel_experience.set()

async def process_travel_experience(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    await state.update_data(travel_experience=message.text)
    await message.answer(_("Пожалуйста, отправьте ваше личное фото:"))
    await OnboardingFormState.waiting_personal_photo.set()

async def process_personal_photo(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    if message.photo:
        file_id = message.photo[-1].file_id
        await state.update_data(personal_photo_id=file_id)
        await message.answer(_("Теперь отправьте фото удостоверения личности:"))
        await OnboardingFormState.waiting_id_card_photo.set()
    else:
        await message.answer(_("Пожалуйста, отправьте фото."))

# Функции для загрузки документов

# Пример обработчика для загрузки фото
async def process_id_card_photo(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer(_("Пожалуйста, отправьте фото или файл."))
        return
    
    await state.update_data(id_card_photo_id=file_id)
    await message.answer(_("Справка о несудимости (адрес):"))
    await OnboardingFormState.waiting_address_proof_photo.set()

# Обработчики для всех документов из Excel
async def process_address_proof_photo(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer(_("Пожалуйста, отправьте фото или файл."))
        return
    
    await state.update_data(address_proof_photo_id=file_id)
    await message.answer(_("Медицинская справка форма 075:"))
    await OnboardingFormState.waiting_health_form_075_photo.set()

async def process_health_form_075_photo(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer(_("Пожалуйста, отправьте фото или файл."))
        return
    
    await state.update_data(health_form_075_photo_id=file_id)
    await message.answer(_("Справка из психоневрологического диспансера:"))
    await OnboardingFormState.waiting_psychoneuro_cert_photo.set()

async def process_psychoneuro_cert_photo(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer(_("Пожалуйста, отправьте фото или файл."))
        return
    
    await state.update_data(psychoneuro_cert_photo_id=file_id)
    await message.answer(_("Справка из наркологического диспансера:"))
    await OnboardingFormState.waiting_narcology_cert_photo.set()

async def process_narcology_cert_photo(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer(_("Пожалуйста, отправьте фото или файл."))
        return
    
    await state.update_data(narcology_cert_photo_id=file_id)
    await message.answer(_("Справка о 20-значном банковском счете:"))
    await OnboardingFormState.waiting_20_digit_account_photo.set()

async def process_20_digit_account_photo(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer(_("Пожалуйста, отправьте фото или файл."))
        return
    
    await state.update_data(account_20_digit_photo_id=file_id)
    await message.answer(_("Диплом об образовании:"))
    await OnboardingFormState.waiting_education_diploma_photo.set()

async def process_education_diploma_photo(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer(_("Пожалуйста, отправьте фото или файл."))
        return
    
    await state.update_data(education_diploma_photo_id=file_id)
    
    # Проверяем, является ли пользователь студентом
    data = await state.get_data()
    if data.get('is_student', '').lower() in ['да', 'yes', 'true']:
        await message.answer(_("Договор с колледжем (для студентов):"))
        await OnboardingFormState.waiting_college_agreement_photo.set()
    else:
        await message.answer(_("Есть ли у вас инвалидность? (Да/Нет)"))
        await OnboardingFormState.waiting_disability_proof_prompt.set()

async def process_college_agreement_photo(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer(_("Пожалуйста, отправьте фото или файл."))
        return
    
    await state.update_data(college_agreement_photo_id=file_id)
    await message.answer(_("Есть ли у вас инвалидность? (Да/Нет)"))
    await OnboardingFormState.waiting_disability_proof_prompt.set()

# Условные документы
async def process_disability_proof_prompt(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    has_disability = message.text.lower() in ['да', 'yes', 'true']
    await state.update_data(has_disability=has_disability)
    
    if has_disability:
        await message.answer(_("Отправьте справку об инвалидности:"))
        await OnboardingFormState.waiting_disability_proof_photo.set()
    else:
        # Проверяем пол для военного билета
        data = await state.get_data()
        if data.get('gender') == 'Мужской':
            await message.answer(_("Есть ли у вас военный билет? (Да/Нет)"))
            await OnboardingFormState.waiting_military_id_prompt.set()
        else:
            await process_final_step(message, state, user)

async def process_disability_proof_photo(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer(_("Пожалуйста, отправьте фото или файл."))
        return
    
    await state.update_data(disability_proof_photo_id=file_id)
    
    # Проверяем пол для военного билета
    data = await state.get_data()
    if data.get('gender') == 'Мужской':
        await message.answer(_("Есть ли у вас военный билет? (Да/Нет)"))
        await OnboardingFormState.waiting_military_id_prompt.set()
    else:
        await process_final_step(message, state, user)

async def process_military_id_prompt(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    has_military_id = message.text.lower() in ['да', 'yes', 'true']
    await state.update_data(has_military_id=has_military_id)
    
    if has_military_id:
        await message.answer(_("Отправьте фото военного билета:"))
        await OnboardingFormState.waiting_military_id_photo.set()
    else:
        await process_final_step(message, state, user)

async def process_military_id_photo(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer(_("Пожалуйста, отправьте фото или файл."))
        return
    
    await state.update_data(military_id_photo_id=file_id)
    await process_final_step(message, state, user)

# Финальный обработчик, который собирает и отправляет данные
async def process_final_step(message: Message, state: FSMContext, user: User):
    _ = message.bot.get("i18n")
    data = await state.get_data()
    
    # 1. Формируем подробный текстовый отчет
    report = f"""
🆕 НОВЫЙ СОТРУДНИК ЗАПОЛНИЛ АНКЕТУ

👤 ЛИЧНЫЕ ДАННЫЕ:
ФИО: {data.get('fio_latin', 'Не указано')}
Дата рождения: {data.get('dob', 'Не указана')}
Место рождения: {data.get('birth_place', 'Не указано')}
Пол: {data.get('gender', 'Не указан')}
Гражданство: {data.get('citizenship', 'Не указано')}
Телефон: {data.get('phone_number', 'Не указан')}
Адрес проживания: {data.get('address_fact', 'Не указан')}
Семейное положение: {data.get('family_status', 'Не указано')}
Дети: {data.get('children_info', 'Не указано')}
Студент: {data.get('is_student', 'Не указано')}

📚 ОБРАЗОВАНИЕ И НАВЫКИ:
Уровень образования: {data.get('education_level', 'Не указан')}
Знание языков: {data.get('languages', 'Не указано')}
Водительские права: {data.get('driver_license', 'Не указано')}

🏥 ЗДОРОВЬЕ:
Проблемы со здоровьем: {data.get('health_issues', 'Не указано')}
Аллергии: {data.get('allergies', 'Не указано')}
Лекарства: {data.get('medications', 'Не указано')}
Курение: {data.get('smoking', 'Не указано')}
Алкоголь: {data.get('alcohol', 'Не указано')}
Судимость: {data.get('criminal_record', 'Не указано')}

💼 РАБОТА И КАРЬЕРА:
Ожидания от первого дня: {data.get('first_day_expectations', 'Не указано')}
Ожидания от работы: {data.get('work_expectations', 'Не указано')}
Карьерные цели: {data.get('career_goals', 'Не указано')}
Предыдущая работа: {data.get('previous_work', 'Не указано')}
Причина увольнения: {data.get('why_quit_previous', 'Не указано')}
Предпочитаемый график: {data.get('work_schedule', 'Не указано')}
Зарплатные ожидания: {data.get('salary_expectations', 'Не указано')}
Мотивация: {data.get('what_motivates', 'Не указано')}
Сильные стороны: {data.get('strengths', 'Не указано')}
Слабые стороны: {data.get('weaknesses', 'Не указано')}
Управление стрессом: {data.get('stress_management', 'Не указано')}
Решение конфликтов: {data.get('conflict_resolution', 'Не указано')}

🎯 ИНТЕРЕСЫ:
Хобби: {data.get('hobby', 'Не указано')}
Любимая музыка: {data.get('favorite_music', 'Не указано')}
Любимые фильмы: {data.get('favorite_movies', 'Не указано')}
Любимые книги: {data.get('favorite_books', 'Не указано')}
Спорт: {data.get('sports', 'Не указано')}
Путешествия: {data.get('travel_experience', 'Не указано')}

📞 КОНТАКТЫ:
Экстренная связь: {data.get('emergency_contact', 'Не указано')}
Instagram: {data.get('instagram', 'Не указано')}

📋 ДОПОЛНИТЕЛЬНО:
Инвалидность: {'Да' if data.get('has_disability') else 'Нет'}
Военный билет: {'Да' if data.get('has_military_id') else 'Нет'}
    """
    
    # 2. Отправляем текстовый отчет HR-менеджеру
    try:
        await message.bot.send_message(HR_CHAT_ID, report)
        
        # 3. Отправляем все загруженные файлы
        await message.bot.send_message(HR_CHAT_ID, " ПРИКРЕПЛЕННЫЕ ДОКУМЕНТЫ:")
        
        documents = [
            ('personal_photo_id', ' Личное фото'),
            ('id_card_photo_id', ' Удостоверение личности'),
            ('address_proof_photo_id', ' Справка о несудимости'),
            ('health_form_075_photo_id', ' Медицинская справка 075'),
            ('psychoneuro_cert_photo_id', ' Справка из психоневрологического диспансера'),
            ('narcology_cert_photo_id', ' Справка из наркологического диспансера'),
            ('account_20_digit_photo_id', ' 20-значный банковский счет'),
            ('education_diploma_photo_id', ' Диплом об образовании'),
            ('college_agreement_photo_id', ' Договор с колледжем'),
            ('disability_proof_photo_id', '♿ Справка об инвалидности'),
            ('military_id_photo_id', ' Военный билет'),
        ]
        
        for doc_key, caption in documents:
            if file_id := data.get(doc_key):
                try:
                    await message.bot.send_document(HR_CHAT_ID, file_id, caption=caption)
                except:
                    try:
                        await message.bot.send_photo(HR_CHAT_ID, file_id, caption=caption)
                    except:
                        await message.bot.send_message(HR_CHAT_ID, f" Ошибка отправки: {caption}")
        
    except Exception as e:
        await message.answer(_("Ошибка отправки данных в HR. Свяжитесь с администратором."))
        print(f"Ошибка отправки в HR: {e}")
    
    # 4. Сообщаем сотруднику об успехе и завершаем
    await message.answer(_(" Отлично! Анкета полностью заполнена и отправлена в HR-отдел. Мы проверим все документы и свяжемся с вами в ближайшее время."))
    await state.finish()

    # 5. Переходим в главное меню стафф-бота
    from service.tgbot.handlers.staff.main import start_handler
    await start_handler(message, user, state)