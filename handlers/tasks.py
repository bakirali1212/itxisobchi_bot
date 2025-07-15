from aiogram import types, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import database

router = Router()

@router.message(F.text == "🛠 Qilingan ishlar")
async def choose_project(msg: types.Message):
    projects = database.get_projects()
    if not projects:
        await msg.answer("Loyihalar topilmadi.")
        return

    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"tasks_{pid}")]
        for pid, name in projects
    ]
    await msg.answer("Qaysi loyihani ko‘rmoqchisiz?", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("tasks_"))
async def show_tasks(callback: types.CallbackQuery):
    pid = int(callback.data.split("_")[1])
    tasks = database.get_tasks_by_project(pid)
    if not tasks:
        await callback.message.answer("Bu loyiha uchun hali hech qanday ish yozilmagan.")
    else:
        text = "\n\n".join([
            f"👤 {user} | 🕒 {time[:16]}\n📌 {task}" for user, task, time in tasks
        ])
        await callback.message.answer(f"🗂 Qilingan ishlar:\n\n{text}")
    await callback.answer()
