#courses.py
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.form_states import FormStates


from keyboards.menu import main_kb, back_to_main_kb

courses_router = Router(name="courses")


# Кнопка "Записаться"
def get_course_inline(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Записаться на курс", callback_data=f"signup:{course_id}")]
        ]
    )


# Открытие раздела "Курсы"
@courses_router.message(F.text == "📚 Курсы")
async def show_courses(message: Message, state: FSMContext):
    await message.answer("<b>📘 Курс 1: Python для начинающих</b>\nНаучись основам программирования с нуля.",
                         reply_markup=get_course_inline(1))
    await message.answer("<b>🎯 Курс 2: Telegram-боты</b>\nСоздание ботов с помощью Aiogram 3.",
                         reply_markup=get_course_inline(2))
    await message.answer("<b>🚀 Курс 3: SQL и базы данных</b>\nРабота с данными и аналитикой.",
                         reply_markup=get_course_inline(3))
    await message.answer("Выберите нужный курс:", reply_markup=back_to_main_kb)


# Обработка кнопки записи на курс
@courses_router.callback_query(F.data.startswith("signup:"))
async def course_callback_handler(callback: CallbackQuery, state: FSMContext):
    course_id = int(callback.data.split(":")[1])

    # Название курса по id
    course_names = {
        1: "Python для начинающих",
        2: "Telegram-боты",
        3: "SQL и базы данных"
    }
    course_title = course_names.get(course_id, "Неизвестный курс")

    # Сохраняем выбранный курс в state
    await state.update_data(course=course_title)
    await state.set_state(FormStates.name)

    # Переходим к форме
    await callback.message.answer(
        f"✅ Вы выбрали курс: <b>{course_title}</b>\n\nВведите своё имя:",
        reply_markup=back_to_main_kb,
        parse_mode="HTML"
    )
    await callback.answer()

