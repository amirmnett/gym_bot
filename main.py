import asyncio
import logging
from aiogram import Bot, Dispatcher
import config
from handlers.auth import auth_router
from handlers.assessment import assessment_router
# فایل‌های دیگر هم بعداً اینجا ایمپورت می‌شوند مثل:
# from handlers.admin import admin_router

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # اضافه کردن روترها (بخش‌های مختلف بات)
    dp.include_router(auth_router)
    dp.include_router(assessment_router)
    # dp.include_router(admin_router)
    
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
