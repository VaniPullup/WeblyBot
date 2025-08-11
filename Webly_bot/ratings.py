from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from db import add_rating
from config import ADMIN_ID

ratings_router = Router()

rate_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⭐", callback_data="rate_1")],
        [InlineKeyboardButton(text="⭐⭐", callback_data="rate_2")],
        [InlineKeyboardButton(text="⭐⭐⭐", callback_data="rate_3")],
        [InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rate_4")],
        [InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rate_5")],
    ]
)


@ratings_router.message(F.text == "⭐ Оценить бота")
async def handle_rating_message(message: Message):
    await message.answer("Пожалуйста, выбери оценку:", reply_markup=rate_kb)


@ratings_router.callback_query(F.data.startswith("rate_"))
async def process_rating_callback(callback: CallbackQuery, bot: Bot):
    rating = int(callback.data.split("_")[1])
    user = callback.from_user

    # Сохраняем в базу
    add_rating(user.id, rating)

    # Отправляем пользователю
    await callback.answer("Спасибо за вашу оценку!")
    await callback.message.answer(f"Вы поставили {rating} ⭐️")

    # 🔔 Уведомляем админа
    username = f"@{user.username}" if user.username else "Без username"
    await bot.send_message(
        ADMIN_ID,
        f"🔔 <b>Новая оценка бота</b>\n"
        f"👤 <code>{user.id}</code>\n"
        f"🔗 {username}\n"
        f"⭐ Оценка: <b>{rating}</b>",
        parse_mode="HTML"
    )
