from aiogram import Router, types, F
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import config  # ⚠️ Buni qo‘shmagansiz, bu muhim!
import database

router = Router()

# Ishchi qo‘shish jarayonini kuzatamiz
waiting_for_worker_id = set()

@router.message(F.text == "/start")
async def start_handler(msg: types.Message):
    # Faqat admin yoki ishchi ro‘yxatda bo‘lsa, botdan foydalanish mumkin
    if msg.from_user.id not in config.ADMIN_ID and not database.is_worker(msg.from_user.id):
        await msg.answer("❌ Uzr, siz ro‘yxatda yo‘qsiz. Botdan faqat ishchilar va adminlar foydalanishi mumkin.")
        return

    buttons = [
        [KeyboardButton(text="📁 Loyihalar")],
        [KeyboardButton(text="🛠 Qilingan ishlar")],
    ]

    # ✅ Admin ID ni config.py dan tekshiramiz
    if msg.from_user.id in config.ADMIN_ID:
        buttons.append([KeyboardButton(text="➕ Loyiha qo‘shish")])
        buttons.append([KeyboardButton(text="👷‍♂️ Ishchilar qo‘shish")])

    markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await msg.answer("Assalomu alaykum! Kerakli bo‘limni tanlang:", reply_markup=markup)

# Admin "Ishchilar qo‘shish" tugmasini bossagina ishchi qo‘shish jarayoni boshlanadi
@router.message(F.text == "👷‍♂️ Ishchilar qo‘shish")
async def ask_worker_id(msg: types.Message):
    if msg.from_user.id not in config.ADMIN_ID:
        await msg.answer("❌ Sizga bu amalni bajarishga ruxsat yo‘q.")
        return
    waiting_for_worker_id.add(msg.from_user.id)
    await msg.answer("🆔 Ishchi Telegram ID raqamini yoki reply orqali foydalanuvchini yuboring:")

@router.message(lambda msg: msg.from_user.id in waiting_for_worker_id)
async def save_worker(msg: types.Message):
    # Foydalanuvchini reply orqali yoki ID orqali olish
    if msg.reply_to_message:
        user = msg.reply_to_message.from_user
        user_id = user.id
        full_name = user.full_name
    else:
        try:
            user_id = int(msg.text.strip())
            full_name = ""
        except Exception:
            await msg.answer("❗ To‘g‘ri Telegram ID yuboring yoki reply qiling.")
            return
    database.add_worker(user_id, full_name)
    waiting_for_worker_id.remove(msg.from_user.id)
    await msg.answer(f"✅ Ishchi qo‘shildi: <code>{user_id}</code>", parse_mode="HTML")
