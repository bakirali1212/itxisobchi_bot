from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, projects, tasks, add_project, feedback

import asyncio

from aiogram import Router, F
from aiogram.types import Message

router = Router()

# faqat private chatlarda ishlaydi
@router.message(F.chat.type == "private")
async def private_handler(message: Message):
    await message.answer("Salom! Bu bot faqat shaxsiy chatda ishlaydi.")

# group yoki supergroupdan kelgan xabarlarni butunlay e'tiborsiz qoldirish
@router.message(F.chat.type.in_(["group", "supergroup"]))
async def ignore_groups(message: Message):
    pass  # hech narsa qilmaydi, javob ham qaytarmaydi



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_routers(
    start.router,
    projects.router,
    tasks.router,
    add_project.router,
    feedback.router
)

async def main():
    print("✅ Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to‘xtadi.")
