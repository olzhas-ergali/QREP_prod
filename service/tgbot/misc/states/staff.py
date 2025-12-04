from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class AuthState(StatesGroup):
    waiting_phone = State()
    waiting_iin = State()


class AuthClientState(StatesGroup):
    waiting_phone = State()
    waiting_name = State()
    waiting_birthday_date = State()
    waiting_gender = State()
    waiting_email = State()


class ProbationPeriodState(StatesGroup):
    first_day = State()
    second_day = State()
    third_day = State()
    fourth_day = State()
    five_day = State()


class OnboardingFormState(StatesGroup):
    # Личные данные
    waiting_fio_latin = State()
    waiting_dob = State()
    waiting_gender = State()
    waiting_phone_number = State()
    waiting_address_fact = State()
    waiting_family_status = State()
    waiting_children_info = State()
    waiting_is_student = State()

    # Дополнительные личные вопросы из Excel
    waiting_birth_place = State()  # Место рождения
    waiting_citizenship = State()  # Гражданство
    waiting_education_level = State()  # Уровень образования
    waiting_languages = State()  # Знание языков
    waiting_driver_license = State()  # Водительские права
    waiting_criminal_record = State()  # Судимость
    waiting_health_issues = State()  # Проблемы со здоровьем
    waiting_allergies = State()  # Аллергии
    waiting_medications = State()  # Принимаемые лекарства
    waiting_smoking = State()  # Курение
    waiting_alcohol = State()  # Употребление алкоголя
    
    # Данные о работе и планах
    waiting_first_day_expectations = State()
    waiting_work_expectations = State()
    waiting_career_goals = State()  # Карьерные цели
    waiting_previous_work = State()  # Предыдущая работа
    waiting_why_quit_previous = State()  # Почему уволились
    waiting_work_schedule = State()  # График работы
    waiting_salary_expectations = State()  # Зарплатные ожидания
    waiting_what_motivates = State()  # Что мотивирует
    waiting_strengths = State()  # Сильные стороны
    waiting_weaknesses = State()  # Слабые стороны
    waiting_stress_management = State()  # Управление стрессом
    waiting_conflict_resolution = State()  # Решение конфликтов
    
    # Личные интересы и контакты
    waiting_hobby = State()
    waiting_emergency_contact = State()
    waiting_instagram = State()
    waiting_favorite_music = State()
    waiting_favorite_movies = State()  # Любимые фильмы
    waiting_favorite_books = State()  # Любимые книги
    waiting_sports = State()  # Спорт
    waiting_travel_experience = State()  # Опыт путешествий
    
    # Фото
    waiting_personal_photo = State()

    # Загрузка документов
    waiting_id_card_photo = State()
    waiting_address_proof_photo = State()  # Справка о несудимости
    waiting_health_form_075_photo = State()  # Медицинская справка 075
    waiting_psychoneuro_cert_photo = State()  # Справка из психоневрологического
    waiting_narcology_cert_photo = State()  # Справка из наркологического
    waiting_20_digit_account_photo = State()  # 20-значный счет
    waiting_education_diploma_photo = State()  # Диплом об образовании
    waiting_college_agreement_photo = State()  # Договор с колледжем
    
    # Условные документы
    waiting_disability_proof_prompt = State()  # Запрос справки об инвалидности
    waiting_disability_proof_photo = State()   # Справка об инвалидности
    
    waiting_military_id_prompt = State()  # Запрос военного билета
    waiting_military_id_photo = State()   # Военный билет
