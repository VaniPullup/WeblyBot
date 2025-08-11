import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton

from config import BOT_TOKEN, ADMIN_ID
from db import init_db, add_rating
from states.form_states import FormStates
from keyboards.menu import back_to_main_kb, main_kb

from handlers import form
from handlers.admin import admin_router
from handlers.courses import show_courses, course_callback_handler, courses_router
from handlers.faq import faq_router
from ratings import ratings_router
from handlers.dialog import dialog_router

# Инициализация бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.admin_id = ADMIN_ID
dp = Dispatcher()

# 🔽 Подключаем в правильном порядке
dp.include_router(faq_router)
dp.include_router(admin_router)
dp.include_router(ratings_router)
dp.include_router(courses_router)
dp.include_router(dialog_router)


# Старт
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "<b>Добро пожаловать в WeblyBot!</b>\n"
        "Выберите нужный раздел из меню ниже.",
        reply_markup=main_kb,
        parse_mode="HTML"
    )


# Оставить заявку
@dp.message(F.text == "📩 Оставить заявку")
async def start_blank_form(message: Message, state: FSMContext):
    await state.update_data(course="— без выбора —")
    await message.answer("Введите своё имя:", reply_markup=back_to_main_kb)
    await state.set_state(FormStates.name)


# Курсы
@dp.message(F.text == "🧑‍🏫 Курсы")
async def open_courses(message: Message, state: FSMContext):
    await show_courses(message, state)


@dp.callback_query(F.data.startswith("enroll_"))
async def cb_course(callback: CallbackQuery, state: FSMContext):
    await course_callback_handler(callback, state)


# Назад из любого места
@dp.message(F.text == "🔙 Назад")
async def back_to_menu(message: Message, state: FSMContext):
    await form.handle_back_button(message, state)


# Назад в меню (универсальный)
@dp.message(F.text == "🔙 Назад в меню")
@dp.message(State("*"), F.text == "🔙 Назад в меню")
async def back_any_state(message: Message, state: FSMContext):
    await form.handle_form_cancel(message, state)


# Обработка шагов формы
@dp.message(FormStates.name)
@dp.message(FormStates.phone)
@dp.message(FormStates.comment)
async def process_form_states(message: Message, state: FSMContext):
    await form.handle_form_input(message, state, ADMIN_ID)


# О компании
@dp.message(F.text == "ℹ️ О компании")
async def about_company(message: Message):
    await message.answer(
        "<b>📌 О компании Webly</b>\n\n"
        "Добро пожаловать в Webly — цифровую платформу, созданную с идеей <i>делать обучение понятным, "
        "а IT-инструменты — доступными</i>.\n\n"
        "🧩 <b>Что мы делаем:</b>\n"
        "— Помогаем освоить Python, Telegram-ботов и базы данных с нуля.\n"
        "— Разрабатываем Telegram-решения под ключ.\n"
        "— Делаем акцент на <u>практике и реальных кейсах</u>.\n\n"
        "🎓 <b>Кому подойдёт:</b>\n"
        "— Начинающим, которые хотят войти в IT.\n"
        "— Бизнесу, которому нужны автоматизация и цифровые решения.\n"
        "— Тем, кто ценит <i>структуру, красоту и результат</i>.\n\n"
        "🤝 <b>Почему нам доверяют:</b>\n"
        "✓ Прямой подход — без воды и бесполезной теории.\n"
        "✓ Уважение к каждому ученику.\n"
        "✓ Честность, визуальный вкус и поддержка на каждом этапе.\n\n"
        "📞 <b>Как связаться:</b>\n"
        "Нажмите кнопку <b>«💬 Написать менеджеру»</b> в главном меню — и мы ответим лично.\n\n"
        "<i>Webly — не просто обучение. Это эстетика. Это внимание к деталям. Это ты, растущий с каждым шагом.</i>\n\n"
        "— С заботой,\n<b>Webly Team</b> 💙",
        parse_mode="HTML"
    )


# Клавиатура с оценками
rating_kb = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text="⭐️ 1"), KeyboardButton(text="⭐️ 2"),
        KeyboardButton(text="⭐️ 3"), KeyboardButton(text="⭐️ 4"),
        KeyboardButton(text="⭐️ 5")
    ]],
    resize_keyboard=True,
    one_time_keyboard=True
)


# Команда /оценить
@dp.message(F.text == "/оценить")
async def rate_bot(message: Message):
    await message.answer("Оцени работу нашего бота по пятибалльной шкале:", reply_markup=rating_kb)


# Обработка оценки
@dp.message(F.text.regexp(r"⭐️ [1-5]"))
async def handle_rating(message: Message):
    rating = int(message.text[-1])
    add_rating(message.from_user.id, rating)
    await message.answer(f"Спасибо за твою оценку: {rating} ⭐️", reply_markup=main_kb)


# Запуск
async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
