import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import config

# ایمپورت تمام روترهایی که تا الان ساختیم
from handlers.auth import auth_router
from handlers.assessment import assessment_router
from handlers.admin import admin_router
from handlers.coach import coach_router
from handlers.inline_search import inline_router
from handlers.athlete import athlete_router
from handlers.plan_creator import plan_router
from handlers.add_exercise import exercise_router
from handlers.media import media_router
from handlers.workout import workout_router

# ایمپورت تسک یادآور
from utils.reminders import check_plans_daily


# --- بخش جدید: سرور وب فیک برای گول زدن رندر ---
async def ping(request):
    return web.Response(text="Bot is running perfectly! 🚀")

async def dummy_web_server():
    app = web.Application()
    app.router.add_get('/', ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # رندر خودش پورت رو میده، اگر نداد روی 10000 تنظیم میشه
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Dummy web server started on port {port}")
# ------------------------------------------------


async def main():
    logging.basicConfig(level=logging.INFO)
    
    # اول سرور فیک رو استارت می‌زنیم تا رندر گیر نده
    await dummy_web_server()
    
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # راه‌اندازی زمان‌بند (Scheduler)
    scheduler = AsyncIOScheduler(timezone='Asia/Tehran')
    scheduler.add_job(check_plans_daily, trigger='cron', hour=8, minute=0, kwargs={'bot': bot})
    scheduler.start()
    
    # اضافه کردن تمام روترها به بات
    dp.include_router(auth_router)
    dp.include_router(assessment_router)
    dp.include_router(admin_router)
    dp.include_router(coach_router)
    dp.include_router(inline_router)
    dp.include_router(athlete_router)
    dp.include_router(plan_router)
    dp.include_router(exercise_router)
    dp.include_router(media_router)
    dp.include_router(workout_router)
    
    print("Bot is starting...")
    # روشن کردن بات
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
