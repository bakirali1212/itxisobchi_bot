from aiogram import types, Router, F
import config
import database

router = Router()

# Bu user loyiha nomini kiritishini kutyaptimi – shuni kuzatamiz
waiting_for_project_name = set()

@router.message(F.text == "➕ Loyiha qo‘shish")
async def ask_project_name(msg: types.Message):
    # Faqat admin kirita oladi
    if msg.from_user.id not in config.ADMIN_ID:
        await msg.answer("❌ Sizga bu amalni bajarishga ruxsat yo‘q.")
        return

    # Admindan loyiha nomini kutamiz
    waiting_for_project_name.add(msg.from_user.id)
    await msg.answer("📝 Yangi loyiha nomini kiriting:")

@router.message(lambda msg: msg.from_user.id in waiting_for_project_name)
async def save_project_name(msg: types.Message):
    project_name = msg.text.strip()

    if not project_name:
        await msg.answer("❗ Loyiha nomi bo‘sh bo‘lishi mumkin emas.")
        return

    # Bazaga qo‘shamiz
    database.add_project(project_name)
    waiting_for_project_name.remove(msg.from_user.id)
    await msg.answer(f"✅ Yangi loyiha qo‘shildi: *{project_name}*", parse_mode="Markdown")
