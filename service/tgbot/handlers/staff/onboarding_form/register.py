# service/tgbot/handlers/staff/onboarding_form/register.py

from aiogram import Dispatcher
from aiogram.types import ContentType
from . import main
from service.tgbot.misc.states.staff import OnboardingFormState
from service.tgbot.keyboards.query_cb import GenderCallback

def register_onboarding_handlers(dp: Dispatcher):
    # Личные данные
    dp.register_message_handler(main.process_fio_latin, state=OnboardingFormState.waiting_fio_latin)
    dp.register_message_handler(main.process_dob, state=OnboardingFormState.waiting_dob)
    dp.register_callback_query_handler(main.process_gender, GenderCallback.filter(), state=OnboardingFormState.waiting_gender)
    dp.register_message_handler(main.process_phone_number, state=OnboardingFormState.waiting_phone_number)
    dp.register_message_handler(main.process_address_fact, state=OnboardingFormState.waiting_address_fact)
    dp.register_message_handler(main.process_family_status, state=OnboardingFormState.waiting_family_status)
    dp.register_message_handler(main.process_children_info, state=OnboardingFormState.waiting_children_info)
    dp.register_message_handler(main.process_is_student, state=OnboardingFormState.waiting_is_student)
    
    # Дополнительные личные данные из Excel
    dp.register_message_handler(main.process_birth_place, state=OnboardingFormState.waiting_birth_place)
    dp.register_message_handler(main.process_citizenship, state=OnboardingFormState.waiting_citizenship)
    dp.register_message_handler(main.process_education_level, state=OnboardingFormState.waiting_education_level)
    dp.register_message_handler(main.process_languages, state=OnboardingFormState.waiting_languages)
    dp.register_message_handler(main.process_driver_license, state=OnboardingFormState.waiting_driver_license)
    dp.register_message_handler(main.process_criminal_record, state=OnboardingFormState.waiting_criminal_record)
    dp.register_message_handler(main.process_health_issues, state=OnboardingFormState.waiting_health_issues)
    dp.register_message_handler(main.process_allergies, state=OnboardingFormState.waiting_allergies)
    dp.register_message_handler(main.process_medications, state=OnboardingFormState.waiting_medications)
    dp.register_message_handler(main.process_smoking, state=OnboardingFormState.waiting_smoking)
    dp.register_message_handler(main.process_alcohol, state=OnboardingFormState.waiting_alcohol)
    
    # Данные о работе и карьере
    dp.register_message_handler(main.process_first_day_expectations, state=OnboardingFormState.waiting_first_day_expectations)
    dp.register_message_handler(main.process_work_expectations, state=OnboardingFormState.waiting_work_expectations)
    dp.register_message_handler(main.process_career_goals, state=OnboardingFormState.waiting_career_goals)
    dp.register_message_handler(main.process_previous_work, state=OnboardingFormState.waiting_previous_work)
    dp.register_message_handler(main.process_why_quit_previous, state=OnboardingFormState.waiting_why_quit_previous)
    dp.register_message_handler(main.process_work_schedule, state=OnboardingFormState.waiting_work_schedule)
    dp.register_message_handler(main.process_salary_expectations, state=OnboardingFormState.waiting_salary_expectations)
    dp.register_message_handler(main.process_what_motivates, state=OnboardingFormState.waiting_what_motivates)
    dp.register_message_handler(main.process_strengths, state=OnboardingFormState.waiting_strengths)
    dp.register_message_handler(main.process_weaknesses, state=OnboardingFormState.waiting_weaknesses)
    dp.register_message_handler(main.process_stress_management, state=OnboardingFormState.waiting_stress_management)
    dp.register_message_handler(main.process_conflict_resolution, state=OnboardingFormState.waiting_conflict_resolution)
    dp.register_message_handler(main.process_hobby, state=OnboardingFormState.waiting_hobby)
    
    # Контакты и интересы
    dp.register_message_handler(main.process_emergency_contact, state=OnboardingFormState.waiting_emergency_contact)
    dp.register_message_handler(main.process_instagram, state=OnboardingFormState.waiting_instagram)
    dp.register_message_handler(main.process_favorite_music, state=OnboardingFormState.waiting_favorite_music)
    dp.register_message_handler(main.process_favorite_movies, state=OnboardingFormState.waiting_favorite_movies)
    dp.register_message_handler(main.process_favorite_books, state=OnboardingFormState.waiting_favorite_books)
    dp.register_message_handler(main.process_sports, state=OnboardingFormState.waiting_sports)
    dp.register_message_handler(main.process_travel_experience, state=OnboardingFormState.waiting_travel_experience)
    
    # Фото
    dp.register_message_handler(main.process_personal_photo, content_types=[ContentType.PHOTO], state=OnboardingFormState.waiting_personal_photo)
    
    # Загрузка документов из Excel
    dp.register_message_handler(main.process_id_card_photo, 
                                content_types=[ContentType.PHOTO, ContentType.DOCUMENT], 
                                state=OnboardingFormState.waiting_id_card_photo)
    dp.register_message_handler(main.process_address_proof_photo, 
                                content_types=[ContentType.PHOTO, ContentType.DOCUMENT], 
                                state=OnboardingFormState.waiting_address_proof_photo)
    dp.register_message_handler(main.process_health_form_075_photo, 
                                content_types=[ContentType.PHOTO, ContentType.DOCUMENT], 
                                state=OnboardingFormState.waiting_health_form_075_photo)
    dp.register_message_handler(main.process_psychoneuro_cert_photo, 
                                content_types=[ContentType.PHOTO, ContentType.DOCUMENT], 
                                state=OnboardingFormState.waiting_psychoneuro_cert_photo)
    dp.register_message_handler(main.process_narcology_cert_photo, 
                                content_types=[ContentType.PHOTO, ContentType.DOCUMENT], 
                                state=OnboardingFormState.waiting_narcology_cert_photo)
    dp.register_message_handler(main.process_20_digit_account_photo, 
                                content_types=[ContentType.PHOTO, ContentType.DOCUMENT], 
                                state=OnboardingFormState.waiting_20_digit_account_photo)
    dp.register_message_handler(main.process_education_diploma_photo, 
                                content_types=[ContentType.PHOTO, ContentType.DOCUMENT], 
                                state=OnboardingFormState.waiting_education_diploma_photo)
    dp.register_message_handler(main.process_college_agreement_photo, 
                                content_types=[ContentType.PHOTO, ContentType.DOCUMENT], 
                                state=OnboardingFormState.waiting_college_agreement_photo)
    
    # Условные документы
    dp.register_message_handler(main.process_disability_proof_prompt, state=OnboardingFormState.waiting_disability_proof_prompt)
    dp.register_message_handler(main.process_disability_proof_photo, 
                                content_types=[ContentType.PHOTO, ContentType.DOCUMENT], 
                                state=OnboardingFormState.waiting_disability_proof_photo)
    dp.register_message_handler(main.process_military_id_prompt, state=OnboardingFormState.waiting_military_id_prompt)
    dp.register_message_handler(main.process_military_id_photo, 
                                content_types=[ContentType.PHOTO, ContentType.DOCUMENT], 
                                state=OnboardingFormState.waiting_military_id_photo)