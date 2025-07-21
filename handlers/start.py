from aiogram import Router, types, F
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import config
import database

router = Router()

# Ishchi qo'shish jarayonini kuzatamiz
waiting_for_worker_id = set()

# Universal bosh sahifa tugmasi
main_menu_btn = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🏠 Bosh sahifa")]], resize_keyboard=True)

# "Noma'lum" so'zini global o'zgaruvchi sifatida saqlash
UNKNOWN_WORKER = "Noma'lum"

@router.message(F.text == "/start")
@router.message(F.text == "🏠 Bosh sahifa")
async def start_handler(msg: types.Message):
    # Foydalanuvchi ishchilar ro'yxatida bo'lsa, ma'lumotlarini saqlaymiz/yangilaymiz
    if database.is_worker(msg.from_user.id):
        full_name = msg.from_user.full_name or (msg.from_user.username or UNKNOWN_WORKER)
        database.save_user(msg.from_user.id, full_name, msg.from_user.username)
        workers = database.get_workers()
        for w in workers:
            if w[0] == msg.from_user.id and (not w[1] or w[1] == UNKNOWN_WORKER):
                database.update_worker_name(msg.from_user.id, full_name)
    
    # Faqat admin yoki ishchi ro'yxatda bo'lsa, botdan foydalanish mumkin
    if msg.from_user.id not in config.ADMIN_ID and not database.is_worker(msg.from_user.id):
        await msg.answer("❌ Uzr, siz ro'yxatda yo'qsiz. Botdan faqat ishchilar va adminlar foydalanishi mumkin.", reply_markup=main_menu_btn)
        return

    buttons = [
        [KeyboardButton(text="📁 Loyihalar")],
        [KeyboardButton(text="🛠 Qilingan ishlar")],
    ]

    # ✅ Admin ID ni config.py dan tekshiramiz
    if msg.from_user.id in config.ADMIN_ID:
        buttons.append([KeyboardButton(text="➕ Loyiha qo'shish")])
        buttons.append([KeyboardButton(text="👷‍♂️ Ishchilar qo'shish")])
        buttons.append([KeyboardButton(text="👥 Ishchilar ro'yxati")])

    markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await msg.answer("Assalomu alaykum! Kerakli bo'limni tanlang:", reply_markup=markup)

# /start tugmasi har doim ishlasin
@router.message(F.text == "/start")
async def always_start(msg: types.Message):
    await start_handler(msg)

@router.message(F.text == "👷‍♂️ Ishchilar qo'shish")
async def ask_worker_id(msg: types.Message):
    if msg.from_user.id not in config.ADMIN_ID:
        await msg.answer("❌ Sizga bu amalni bajarishga ruxsat yo'q.", reply_markup=main_menu_btn)
        return
    waiting_for_worker_id.add(msg.from_user.id)
    await msg.answer("🆔 Ishchi Telegram ID raqamini yoki reply orqali foydalanuvchini yuboring:", reply_markup=main_menu_btn)

@router.message(lambda msg: msg.from_user.id in waiting_for_worker_id)
async def save_worker(msg: types.Message):
    if msg.reply_to_message:
        user = msg.reply_to_message.from_user
        user_id = user.id
        full_name = user.full_name
        database.add_worker(user_id, full_name)
        waiting_for_worker_id.remove(msg.from_user.id)
        await msg.answer(f"✅ Ishchi qo'shildi: <b>{full_name}</b> (<code>{user_id}</code>)", parse_mode="HTML", reply_markup=main_menu_btn)
    else:
        try:
            user_id = int(msg.text.strip())
            # Foydalanuvchi /start bosmagan bo'lsa ham qo'shamiz
            database.add_worker(user_id, UNKNOWN_WORKER)
            waiting_for_worker_id.remove(msg.from_user.id)
            await msg.answer(f"✅ Ishchi ID (<code>{user_id}</code>) ro'yxatga qo'shildi. Foydalanuvchi /start bosganda ismi avtomatik yangilanadi.", parse_mode="HTML", reply_markup=main_menu_btn)
        except Exception:
            await msg.answer("❗ To'g'ri Telegram ID yuboring yoki reply qiling.", reply_markup=main_menu_btn)
            return

# Admin uchun ishchilar ro'yxatini ko'rsatish
def format_workers_list():
    workers = database.get_workers()
    if not workers:
        return "Ishchilar ro'yxati bo'sh."
    return '\n'.join([f"<b>{w[1] if w[1] else UNKNOWN_WORKER}</b> (<code>{w[0]}</code>)" for w in workers])

@router.message(F.text == "👥 Ishchilar ro'yxati")
async def show_workers(msg: types.Message):
    if msg.from_user.id not in config.ADMIN_ID:
        await msg.answer("❌ Sizga bu amalni bajarishga ruxsat yo'q.", reply_markup=main_menu_btn)
        return
    text = format_workers_list()
    await msg.answer(f"<b>Ishchilar ro'yxati:</b>\n\n{text}", parse_mode="HTML", reply_markup=main_menu_btn)
