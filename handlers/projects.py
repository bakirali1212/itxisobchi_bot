from aiogram import types, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import database
import config

router = Router()
waiting_task = {}

@router.message(F.text == "📁 Loyihalar")
async def show_projects(msg: types.Message):
    projects = database.get_projects()
    if not projects:
        await msg.answer("Hozircha hech qanday loyiha yo‘q.")
        return

    buttons = []
    for pid, name in projects:
        row = [InlineKeyboardButton(text=name, callback_data=f"project_{pid}")]
        # Faqat admin uchun o‘chirish tugmasi
        if msg.from_user.id in config.ADMIN_ID:
            row.append(InlineKeyboardButton(text="❌ O‘chirish", callback_data=f"deleteproj_{pid}"))
        buttons.append(row)
    await msg.answer("Loyihani tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("project_"))
async def select_project(callback: types.CallbackQuery):
    pid = int(callback.data.split("_")[1])
    waiting_task[callback.from_user.id] = pid
    await callback.message.answer("Ushbu loyiha uchun nima ish qildingiz?")
    await callback.answer()

@router.message(lambda msg: msg.from_user.id in waiting_task)
async def save_task(msg: types.Message):
    pid = waiting_task.pop(msg.from_user.id)

    # 🔸 Bazaga saqlaymiz
    database.add_task(pid, msg.from_user.id, msg.from_user.full_name, msg.text)
    await msg.answer("✅ Ish muvaffaqiyatli saqlandi.")

    # 🔹 Guruhga yuboramiz
    text = (
        f"📢 *Yangi bajarilgan ish!*\n\n"
        f"👤 Foydalanuvchi: [{msg.from_user.full_name}](tg://user?id={msg.from_user.id})\n"
        f"📂 Loyiha ID: {pid}\n"
        f"📌 Ish: {msg.text}"
    )
    await msg.bot.send_message(config.GROUP_ID, text, parse_mode="Markdown")

# Loyihani o‘chirish tugmasi uchun callback
@router.callback_query(F.data.startswith("deleteproj_"))
async def confirm_delete_project(callback: types.CallbackQuery):
    if callback.from_user.id not in config.ADMIN_ID:
        await callback.answer("Ruxsat yo‘q", show_alert=True)
        return
    pid = int(callback.data.split("_")[1])
    # Tasdiqlash uchun tugmalar
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, o‘chirilsin", callback_data=f"confirmdel_{pid}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_del")
        ]
    ])
    await callback.message.answer("Loyihani o‘chirishni tasdiqlaysizmi?", reply_markup=markup)
    await callback.answer()

# Tasdiqlashdan so‘ng o‘chirish
@router.callback_query(F.data.startswith("confirmdel_"))
async def delete_project_handler(callback: types.CallbackQuery):
    if callback.from_user.id not in config.ADMIN_ID:
        await callback.answer("Ruxsat yo‘q", show_alert=True)
        return
    pid = int(callback.data.split("_")[1])
    database.delete_project(pid)
    await callback.message.answer("✅ Loyiha va unga tegishli ishlar o‘chirildi.")
    # Loyihalar ro‘yxatini yangilash
    projects = database.get_projects()
    if not projects:
        await callback.message.answer("Hozircha hech qanday loyiha yo‘q.")
        return
    buttons = []
    for pid, name in projects:
        row = [InlineKeyboardButton(text=name, callback_data=f"project_{pid}")]
        if callback.from_user.id in config.ADMIN_ID:
            row.append(InlineKeyboardButton(text="❌ O‘chirish", callback_data=f"deleteproj_{pid}"))
        buttons.append(row)
    await callback.message.answer("Loyihani tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

# Bekor qilish tugmasi
@router.callback_query(F.data == "cancel_del")
async def cancel_delete(callback: types.CallbackQuery):
    await callback.message.answer("❌ O‘chirish bekor qilindi.")
    await callback.answer()
