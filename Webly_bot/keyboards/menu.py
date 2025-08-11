from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# 📍 Главное меню
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📩 Оставить заявку")],
        [KeyboardButton(text="🧑‍🏫 Курсы")],
        [KeyboardButton(text="❓ FAQ")],
        [KeyboardButton(text="💬 Написать менеджеру")],
        [KeyboardButton(text="⭐ Оценить бота")],
        [KeyboardButton(text="ℹ️ О компании")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие:"
)

# 🔙 Кнопка назад в меню (универсальная)
back_to_main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Назад в меню")]],
    resize_keyboard=True
)

# 🔘 Inline-кнопка "Записаться на курс"
def get_course_inline(course_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📝 Записаться на курс", callback_data=f"enroll_{course_name}")
    ]])

# 🔘 Inline-кнопка "Назад к курсам"
def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_courses")
    ]])
