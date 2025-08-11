#broadcast.py
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from db import get_all_leads
import asyncio

class BroadcastStates(StatesGroup):
    waiting_for_message = State()

broadcast_router = Router()

@broadcast_router.message(Command("рассылка"))
async def start_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != int(message.bot.admin_id):
        await message.answer("⛔ Доступ запрещён.")
        return
    await state.set_state(BroadcastStates.waiting_for_message)
    await message.answer("Введите текст для рассылки:")

@broadcast_router.message(BroadcastStates.waiting_for_message)
async def send_broadcast(message: Message, state: FSMContext):
    await state.clear()
    text = message.text
    users = get_all_leads()

    # Собираем уникальные user_id
    unique_ids = set()
    for user in users:
        unique_ids.add(user[5])  # user_id — это 6-й столбец

    sent, failed = 0, 0

    for uid in unique_ids:
        try:
            await message.bot.send_message(uid, text)
            await asyncio.sleep(0.05)
            sent += 1
        except Exception as e:
            failed += 1
            print(f"[Ошибка отправки]: {e}")

    await message.answer(f"📬 Рассылка завершена.\nУспешно: {sent}\nНе доставлено: {failed}")
