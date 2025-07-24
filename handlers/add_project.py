from aiogram import types, Router, F
import config
import database
from handlers.start import main_menu_btn
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

# Orqaga tugmasi
back_btn = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⬅️ Orqaga")]], resize_keyboard=True)

# Bu user loyiha nomini kiritishini kutyaptimi – shuni kuzatamiz
waiting_for_project_name = set()

@router.message(F.text == "➕ Loyiha qo'shish")
async def ask_project_name(msg: types.Message):
    # Faqat admin kirita oladi
    if msg.from_user.id not in config.ADMIN_ID:
        await msg.answer("❌ Sizga bu amalni bajarishga ruxsat yo‘q.", reply_markup=back_btn)
        return

    # Admindan loyiha nomini kutamiz
    waiting_for_project_name.add(msg.from_user.id)
    await msg.answer("📝 Yangi loyiha nomini kiriting:", reply_markup=back_btn)

@router.message(F.text == "⬅️ Orqaga")
async def back_to_main(msg: types.Message):
    from handlers.start import start_handler
    await start_handler(msg)

@router.message(lambda msg: msg.from_user.id in waiting_for_project_name)
async def save_project_name(msg: types.Message):
    project_name = msg.text.strip()

    if not project_name:
        await msg.answer("❗ Loyiha nomi bo‘sh bo‘lishi mumkin emas.", reply_markup=back_btn)
        return

    # Bazaga qo‘shamiz
    database.add_project(project_name)
    waiting_for_project_name.remove(msg.from_user.id)
    await msg.answer(f"✅ Yangi loyiha qo‘shildi: *{project_name}*", parse_mode="Markdown", reply_markup=back_btn)
