from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID

dialog_router = Router()

class DialogStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_admin_reply = State()
    admin_reply_user_id = State()

@dialog_router.message(F.text == "💬 Написать менеджеру")
async def ask_user_message(message: Message, state: FSMContext):
    await state.set_state(DialogStates.waiting_for_message)
    await message.answer("✍️ Напиши своё сообщение, и менеджер ответит тебе в ближайшее время.")

@dialog_router.message(DialogStates.waiting_for_message)
async def forward_to_admin(message: Message, state: FSMContext):
    user = message.from_user
    user_id = user.id
    text = message.text

    msg = (
        f"📩 <b>Новое сообщение от клиента:</b>\n\n"
        f"<b>Имя:</b> {user.full_name}\n"
        f"<b>Username:</b> @{user.username or '—'}\n"
        f"<b>User ID:</b> <code>{user_id}</code>\n\n"
        f"<b>Сообщение:</b>\n{text}"
    )

    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Ответить", callback_data=f"replyto_{user_id}")]
    ])

    try:
        await message.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="HTML", reply_markup=reply_kb)
        await message.answer("✅ Твоё сообщение отправлено менеджеру.")
    except Exception as e:
        await message.answer("❌ Не удалось отправить сообщение.")
        print(f"[Ошибка при пересылке админу]: {e}")

    await state.clear()

@dialog_router.callback_query(F.data.startswith("replyto_"))
async def start_reply(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.replace("replyto_", ""))
    await state.update_data(admin_reply_user_id=user_id)
    await state.set_state(DialogStates.waiting_for_admin_reply)
    await callback.message.answer("💬 Напиши сообщение, которое будет отправлено клиенту.")
    await callback.answer()

@dialog_router.message(DialogStates.waiting_for_admin_reply)
async def send_admin_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("admin_reply_user_id")
    try:
        await message.bot.send_message(chat_id=user_id, text=message.text)
        await message.answer("✅ Сообщение отправлено клиенту.")
    except Exception as e:
        await message.answer("❌ Не удалось отправить сообщение клиенту.")
        print(f"[Ошибка отправки клиенту]: {e}")
    await state.clear()
