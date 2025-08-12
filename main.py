from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, projects, tasks, add_project, feedback

import asyncio

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
