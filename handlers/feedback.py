from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import database
import config

router = Router()
waiting_feedback = {}

# Orqaga tugmasi
back_btn = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⬅️ Orqaga")]], resize_keyboard=True)

@router.message(F.text == "📌 Talab va Taklif")
async def ask_feedback(msg: types.Message):
    waiting_feedback[msg.from_user.id] = True
    await msg.answer("Iltimos, talab yoki taklifingizni yozib qoldiring:", reply_markup=back_btn)


@router.message(lambda m: m.from_user.id in waiting_feedback and m.text not in ["⬅️ Orqaga", "📋 Talab va Takliflarni ko'rish"])
async def save_feedback_handler(msg: types.Message):
    waiting_feedback.pop(msg.from_user.id, None)
    username = msg.from_user.username or msg.from_user.full_name
    database.save_feedback(msg.from_user.id, username, msg.text)
    await msg.answer("✅ Taklifingiz saqlandi. Rahmat!", reply_markup=back_btn)


@router.message(F.text == "📋 Talab va Takliflarni ko'rish")
async def show_feedback(msg: types.Message):
    if msg.from_user.id not in config.ADMIN_ID:
        await msg.answer("❌ Bu bo‘lim faqat adminlar uchun.")
        return

    feedbacks = database.get_all_feedback()
    if not feedbacks:
        await msg.answer("Hozircha talab yoki taklif yo‘q.", reply_markup=back_btn)
        return

    # feedback tuple -> (username, message)
    text = "\n\n".join([f"{f[0]}: {f[1]}" for f in feedbacks])
    await msg.answer(text, reply_markup=back_btn)
