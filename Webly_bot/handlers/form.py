#form.py
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message

from db import save_lead
from keyboards.menu import main_kb, back_to_main_kb
from states.form_states import FormStates


async def handle_form_input(message: Message, state: FSMContext, admin_id: int):
    current_state = await state.get_state()

    if current_state == FormStates.name:
        await state.update_data(name=message.text)
        await message.answer("Теперь введите номер телефона:", reply_markup=back_to_main_kb)
        await state.set_state(FormStates.phone)
        return

    if current_state == FormStates.phone:
        await state.update_data(phone=message.text)
        await message.answer("Есть ли у вас комментарий или пожелание? Если нет — напишите «-».",
                             reply_markup=back_to_main_kb)
        await state.set_state(FormStates.comment)
        return

    if current_state == FormStates.comment:
        await state.update_data(comment=message.text)
        data = await state.get_data()

        log_msg = (f"[ЗАЯВКА]\nКурс: {data.get('course')}\nИмя: {data.get('name')}\nТелефон: {data.get('phone')}\n"
                   f"Комментарий: {data.get('comment')}")
        print(log_msg)

        msg = (
            f"\U0001F4C9 <b>Новая заявка!</b>\n\n"
            f"\U0001F393 <b>Курс:</b> {data.get('course')}\n"
            f"\U0001F464 <b>Имя:</b> {data.get('name')}\n"
            f"\U0001F4DE <b>Телефон:</b> {data.get('phone')}\n"
            f"\U0001F517 <b>Telegram:</b> @{message.from_user.username or '—'}\n"
            f"\U0001F194 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
            f"\U0001F4CC <b>Статус:</b> <code>новая</code>\n"
            f"\U0001F4AC <b>Комментарий:</b> {data.get('comment')}"
        )

        try:
            save_lead({
                "name": data.get("name"),
                "phone": data.get("phone"),
                "course": data.get("course"),
                "telegram": message.from_user.username or "—",
                "user_id": message.from_user.id,
                "comment": data.get("comment")
            })
        except Exception as e:
            print(f"[ОШИБКА СОХРАНЕНИЯ В БАЗУ]: {e}")
            await state.clear()
            return

        # Получаем ID только что добавленной заявки
        import sqlite3
        from db import DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM leads WHERE user_id = ? ORDER BY id DESC LIMIT 1", (message.from_user.id,))
        result = cursor.fetchone()
        conn.close()
        lead_id = result[0] if result else None

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👷 Принять в работу", callback_data=f"assign_{lead_id}")]
        ])


        await message.bot.send_message(chat_id=admin_id, text=msg, reply_markup=kb)
        await message.answer(
            "🎉 <b>Спасибо! Мы получили вашу заявку.</b>\n"
            "Наш менеджер скоро свяжется с вами. А пока можете посмотреть другие курсы 👇",
            parse_mode="HTML",
            reply_markup=main_kb
        )

        await message.answer(
            "📚 Вы можете выбрать нужный раздел в меню ниже.",
            reply_markup=main_kb
        )

        try:
            save_lead({
                "name": data.get("name"),
                "phone": data.get("phone"),
                "course": data.get("course"),
                "telegram": message.from_user.username or "—",
                "user_id": message.from_user.id,
                "comment": data.get("comment")
            })
        except Exception as e:
            print(f"[ОШИБКА СОХРАНЕНИЯ В БАЗУ]: {e}")

        await state.clear()
        return


async def handle_back_button(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_kb)


async def handle_form_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_kb)
