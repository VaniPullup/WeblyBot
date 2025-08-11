#admin.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_all_leads, search_leads
import asyncio
import sqlite3
from db import DB_PATH


admin_router = Router()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_search_query = State()
    waiting_for_status_change_id = State()
    waiting_for_new_status = State()
    waiting_for_clear_confirm = State()
    waiting_for_reply_text = State()

STATUS_MAP = {
    "new": "новая",
    "in_progress": "в работе",
    "done": "обработана"
}

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != int(message.bot.admin_id):
        await message.answer("⛔ Доступ запрещён.")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📂 Все заявки", callback_data="view_leads"),
            InlineKeyboardButton(text="🗑 Очистить заявки", callback_data="clear_leads")
        ],
        [InlineKeyboardButton(text="🔎 Поиск по заявкам", callback_data="search_leads")],
        [InlineKeyboardButton(text="📥 Заявки по статусу", callback_data="filter_by_status")],
        [InlineKeyboardButton(text="🔁 Изменить статус заявки", callback_data="change_status")],
        [InlineKeyboardButton(text="📤 Сделать рассылку", callback_data="broadcast")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="show_stats")],  # ✅ добавлено
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_admin")]
    ])

    await message.answer("<b>🔧 Админ-панель:</b>\nВыбери действие:", reply_markup=kb)

@admin_router.callback_query(F.data == "clear_leads")
async def ask_clear_confirm(callback: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, очистить", callback_data="confirm_clear_leads"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_clear_leads")
        ]
    ])
    await state.set_state(AdminStates.waiting_for_clear_confirm)
    await callback.message.answer("Вы уверены, что хотите удалить все заявки?", reply_markup=kb)
    await callback.answer()

@admin_router.callback_query(F.data == "confirm_clear_leads")
async def clear_all_leads(callback: CallbackQuery, state: FSMContext):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads")
    conn.commit()
    conn.close()
    await state.clear()
    await callback.message.answer("🗑 Все заявки были удалены.")
    await callback.answer()

@admin_router.callback_query(F.data == "cancel_clear_leads")
async def cancel_clear(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Очистка отменена.")
    await callback.answer()

@admin_router.callback_query(F.data == "close_admin")
async def close_admin_menu(callback: CallbackQuery):
    await callback.message.delete()

@admin_router.callback_query(F.data == "view_leads")
async def view_all_leads(callback: CallbackQuery):
    leads = get_all_leads()
    if not leads:
        await callback.message.answer("Нет заявок.")
        return
    for lead in leads:
        await send_lead(callback.message, lead)

@admin_router.callback_query(F.data == "search_leads")
async def ask_search_query(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_search_query)
    await callback.message.answer("Введите ключевое слово для поиска:")
    await callback.answer()

@admin_router.message(AdminStates.waiting_for_search_query)
async def do_search(message: Message, state: FSMContext):
    await state.clear()
    query = message.text.strip()
    results = search_leads(query)
    if not results:
        await message.answer("Ничего не найдено.")
        return
    for lead in results:
        await send_lead(message, lead)

@admin_router.callback_query(F.data == "broadcast")
async def ask_broadcast_text(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.message.answer("Введите текст для рассылки:")
    await callback.answer()

@admin_router.message(AdminStates.waiting_for_broadcast)
async def do_broadcast(message: Message, state: FSMContext):
    await state.clear()
    text = message.text
    leads = get_all_leads()
    unique_ids = set(lead[5] for lead in leads)
    sent, failed = 0, 0
    for uid in unique_ids:
        try:
            await message.bot.send_message(uid, text)
            await asyncio.sleep(0.05)
            sent += 1
        except Exception as e:
            print(f"[Ошибка отправки]: {e}")
            failed += 1
    await message.answer(f"📬 Рассылка завершена.\nУспешно: {sent}\nНе доставлено: {failed}")

@admin_router.callback_query(F.data == "filter_by_status")
async def show_status_filter(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Новые", callback_data="status_new")],
        [InlineKeyboardButton(text="🛠 В работе", callback_data="status_in_progress")],
        [InlineKeyboardButton(text="✅ Обработанные", callback_data="status_done")]
    ])
    await callback.message.answer("Выберите статус заявок для отображения:", reply_markup=kb)

@admin_router.callback_query(F.data.startswith("status_"))
async def show_leads_by_status(callback: CallbackQuery):
    status = STATUS_MAP[callback.data.replace("status_", "")]
    leads = get_all_leads()
    filtered = [l for l in leads if l[6] == status]
    if not filtered:
        await callback.message.answer(f"Нет заявок со статусом: {status}")
        return
    for lead in filtered:
        await send_lead(callback.message, lead)

@admin_router.callback_query(F.data == "change_status")
async def ask_for_id_to_change(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_status_change_id)
    await callback.message.answer("Введите <b>ID заявки</b> для изменения статуса:", parse_mode="HTML")
    await callback.answer()

@admin_router.message(AdminStates.waiting_for_status_change_id)
async def get_lead_and_choose_status(message: Message, state: FSMContext):
    await state.update_data(change_lead_id=message.text.strip())
    leads = get_all_leads()
    lead = next((l for l in leads if str(l[0]) == message.text.strip()), None)
    if not lead:
        await state.clear()
        await message.answer("❌ Заявка с таким ID не найдена.")
        return
    await send_lead(message, lead)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Новая", callback_data="setstatus_new")],
        [InlineKeyboardButton(text="🛠 В работе", callback_data="setstatus_in_progress")],
        [InlineKeyboardButton(text="✅ Обработана", callback_data="setstatus_done")]
    ])
    await state.set_state(AdminStates.waiting_for_new_status)
    await message.answer("Выберите новый статус:", reply_markup=kb)

@admin_router.callback_query(F.data.startswith("setstatus_"))
async def set_new_status(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lead_id = data.get("change_lead_id")
    new_status = STATUS_MAP[callback.data.replace("setstatus_", "")]
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (new_status, lead_id))
    conn.commit()
    conn.close()
    await callback.message.answer(f"✅ Статус заявки ID {lead_id} обновлён на: <b>{new_status}</b>", parse_mode="HTML")
    await state.clear()
    await callback.answer()

@admin_router.callback_query(F.data.startswith("assign_"))
async def assign_lead(callback: CallbackQuery):
    lead_id = callback.data.replace("assign_", "")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET status = ? WHERE id = ?", ("в работе", lead_id))
    conn.commit()
    conn.close()
    leads = get_all_leads()
    lead = next((l for l in leads if str(l[0]) == lead_id), None)
    if not lead:
        await callback.message.answer("❌ Заявка не найдена.")
        return
    text = (
        f"<b>🆔 ID заявки:</b> {lead[0]}\n"
        f"<b>Имя:</b> {lead[1]}\n"
        f"<b>Телефон:</b> {lead[2]}\n"
        f"<b>Курс:</b> {lead[3]}\n"
        f"<b>Telegram:</b> @{lead[4]}\n"
        f"<b>User ID:</b> <code>{lead[5]}</code>\n"
        f"<b>Статус:</b> <code>в работе</code>\n"
        f"<b>Комментарий:</b> {lead[7]}\n"
        f"<b>Дата:</b> {lead[8]}"
    )
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer("🛠 Статус заявки изменён на 'в работе'")

@admin_router.callback_query(F.data.startswith("replyto_"))
async def start_reply(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.replace("replyto_", ""))
    await state.update_data(reply_user_id=user_id)
    await state.set_state(AdminStates.waiting_for_reply_text)
    await callback.message.answer(
        f"💬 <b>Ответ пользователю:</b>\n"
        f"Сейчас напиши текст, который я отправлю ему от имени бота.",
        parse_mode="HTML"
    )
    await callback.answer()


@admin_router.message(AdminStates.waiting_for_reply_text)
async def send_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("reply_user_id")
    try:
        await message.bot.send_message(chat_id=user_id, text=message.text)
        await message.answer("✅ <b>Сообщение отправлено клиенту.</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer(
            f"❌ <b>Не удалось отправить сообщение.</b>\n"
            f"<code>{e}</code>",
            parse_mode="HTML"
        )
    await state.clear()

from db import get_all_ratings

@admin_router.callback_query(F.data == "show_stats")
async def show_stats_callback(callback: CallbackQuery):
    if callback.from_user.id != int(callback.bot.admin_id):
        await callback.answer("⛔ Доступ запрещён.", show_alert=True)
        return

    ratings = get_all_ratings()
    if not ratings:
        await callback.message.answer("Нет оценок.")
        await callback.answer()
        return

    stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for _, rate in ratings:
        stats[rate] += 1

    text = "<b>📊 Статистика оценок бота:</b>\n"
    for i in range(1, 6):
        text += f"{i}⭐ — <b>{stats[i]}</b>\n"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()



async def send_lead(destination, lead):
    text = (
        f"<b>🆔 ID заявки:</b> {lead[0]}\n"
        f"<b>Имя:</b> {lead[1]}\n"
        f"<b>Телефон:</b> {lead[2]}\n"
        f"<b>Курс:</b> {lead[3]}\n"
        f"<b>Telegram:</b> @{lead[4]}\n"
        f"<b>User ID:</b> <code>{lead[5]}</code>\n"
        f"<b>Статус:</b> <code>{lead[6]}</code>\n"
        f"<b>Комментарий:</b> {lead[7]}\n"
        f"<b>Дата:</b> {lead[8]}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Ответить", callback_data=f"replyto_{lead[5]}")]
    ])
    await destination.answer(text, parse_mode="HTML", reply_markup=kb)

