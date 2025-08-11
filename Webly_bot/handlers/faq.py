#faq.py
from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards.menu import main_kb

faq_router = Router(name="faq")

FAQ_DATA = {
    "📌 Как оплатить курс?": "Вы можете оплатить курс с помощью карты любого банка. После записи мы отправим вам инструкцию по оплате.",
    "📍 Где проходят занятия?": "Все занятия проходят онлайн — в удобной платформе, доступной с телефона или компьютера.",
    "⏱ Сколько длится курс?": "В среднем курс длится от 3 до 6 недель. Всё зависит от выбранной программы.",
    "📲 Можно ли учиться с телефона?": "Да, вся платформа полностью адаптирована под мобильные устройства.",
    "🎓 Есть ли сертификат?": "По окончании курса вы получите электронный сертификат об обучении.",
    "🤔 Что делать, если возникнут вопросы?": "Вы всегда можете написать нашему менеджеру через раздел «💬 Написать менеджеру».",
    "🧠 Можно ли потом доработать бота?": "Да. Архитектура гибкая — мы можем добавить любые функции в будущем.",
    "💵 Сколько стоит разработка?": "Простой бот — от 7 000₽. Полный функционал — 15 000–35 000₽. Всё зависит от задач.",
    "🔐 Бот безопасен?": "Да. Мы используем надёжные технологии, данные хранятся на вашем сервере.",
    "📞 Как быстро отвечаете?": "Мы стараемся отвечать в течение 1–2 часов в рабочее время.",
}

def build_faq_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for question in FAQ_DATA.keys():
        builder.button(text=question)
    builder.button(text="🔙 Назад в меню")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

@faq_router.message(F.text == "❓ FAQ")
async def open_faq(message: Message):
    await message.answer(
        "<b>🧠 Часто задаваемые вопросы</b>\n\n"
        "Нажми на интересующий вопрос, и я покажу ответ:",
        reply_markup=build_faq_keyboard()
    )

@faq_router.message(F.text.in_(FAQ_DATA.keys()))
async def send_faq_answer(message: Message):
    answer = FAQ_DATA[message.text]
    await message.answer(f"<b>{message.text}</b>\n\n{answer}")

@faq_router.message(F.text == "🔙 Назад в меню")
async def back_to_main(message: Message):
    await message.answer("🔙 Возврат в главное меню.", reply_markup=main_kb)
