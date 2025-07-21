from aiogram import types, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import database
from handlers.start import main_menu_btn

router = Router()

# Orqaga tugmasi
back_btn = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⬅️ Orqaga")]], resize_keyboard=True)

@router.message(F.text == "🛠 Qilingan ishlar")
async def choose_project(msg: types.Message):
    projects = database.get_projects()
    if not projects:
        await msg.answer("Loyihalar topilmadi.", reply_markup=back_btn)
        return

    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"tasks_{pid}")]
        for pid, name in projects
    ]
    await msg.answer("Qaysi loyihani ko‘rmoqchisiz?", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await msg.answer("⬅️ Orqaga qaytish uchun tugmani bosing", reply_markup=back_btn)

@router.message(F.text == "⬅️ Orqaga")
async def back_to_main(msg: types.Message):
    from handlers.start import start_handler
    await start_handler(msg)

@router.callback_query(F.data.startswith("tasks_"))
async def show_tasks(callback: types.CallbackQuery):
    pid = int(callback.data.split("_")[1])
    tasks = database.get_tasks_by_project(pid)
    if not tasks:
        await callback.message.answer("Bu loyiha uchun hali hech qanday ish yozilmagan.", reply_markup=back_btn)
    else:
        text = "\n\n".join([
            f"👤 {user} | 🕒 {time[:16]}\n📌 {task}" for user, task, time in tasks
        ])
        await callback.message.answer(f"🗂 Qilingan ishlar:\n\n{text}", reply_markup=back_btn)
    await callback.answer()
