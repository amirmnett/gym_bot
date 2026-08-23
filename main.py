import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import config

# ایمپورت روترها
from handlers.auth import auth_router
from handlers.assessment import assessment_router
from handlers.admin import admin_router
from handlers.coach import coach_router
from handlers.inline_search import inline_router
from handlers.athlete import athlete_router
from handlers.plan_creator import plan_router 
from handlers.add_exercise import exercise_router
# ایمپورت تسک یادآور
from utils.reminders import check_plans_daily
from handlers.workout import workout_router

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # راه‌اندازی زمان‌بند (Scheduler)
    scheduler = AsyncIOScheduler(timezone='Asia/Tehran')
    # تنظیم اجرای تابع یادآور هر روز ساعت ۸ صبح
    scheduler.add_job(check_plans_daily, trigger='cron', hour=8, minute=0, kwargs={'bot': bot})
    scheduler.start()
    
    # اضافه کردن روترها
    dp.include_router(auth_router)
    dp.include_router(assessment_router)
    dp.include_router(admin_router)
    dp.include_router(coach_router)
    dp.include_router(inline_router)
    dp.include_router(athlete_router)
    dp.include_router(plan_router) # اضافه شد
    dp.include_router(exercise_router)
    dp.include_router(workout_router)
    
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
