import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_expiring_plans, get_user

async def check_plans_daily(bot: Bot):
    logging.info("Checking for expiring plans...")
    
    # --- بررسی برنامه‌هایی که ۷ روز به پایانشان مانده ---
    plans_7_days = get_expiring_plans(days_left=7)
    for plan in plans_7_days:
        athlete = get_user(plan['athlete_id'])
        athlete_name = athlete['name'] if athlete else "ورزشکار"
        
        # پیام به شاگرد
        try:
            await bot.send_message(
                chat_id=plan['athlete_id'],
                text="⏳ **یادآوری:** فقط ۷ روز تا پایان برنامه‌ی فعلی‌ات باقی مونده! پرقدرت ادامه بده."
            )
        except Exception: pass
        
        # پیام به مربی
        try:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✍️ نوشتن برنامه جدید", callback_data=f"newplan_{plan['athlete_id']}")]
            ])
            await bot.send_message(
                chat_id=plan['coach_id'],
                text=f"🔔 **آلارم آمادگی:**\nفقط ۷ روز به پایان برنامه‌ی شاگردت (**{athlete_name}**) مونده. می‌تونی از الان برای فاز بعدی برنامه‌اش رو آماده کنی.",
                reply_markup=keyboard
            )
        except Exception: pass


    # --- بررسی برنامه‌هایی که دقیقاً امروز تمام می‌شوند ---
    plans_today = get_expiring_plans(days_left=0)
    for plan in plans_today:
        athlete = get_user(plan['athlete_id'])
        athlete_name = athlete['name'] if athlete else "ورزشکار"
        
        try:
            await bot.send_message(
                chat_id=plan['athlete_id'],
                text="🏁 **پایان برنامه:** خسته نباشی قهرمان! دوره‌ی تمرینی تو امروز رسماً تموم شد. منتظر برنامه جدید مربی باش."
            )
        except Exception: pass
        
        try:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🟢 برنامه دیلود (ریکاوری)", callback_data=f"newplan_{plan['athlete_id']}")]
            ])
            await bot.send_message(
                chat_id=plan['coach_id'],
                text=f"🚨 **پایان دوره:**\nبرنامه‌ی شاگردت (**{athlete_name}**) امروز تمام شد! حتماً براش برنامه‌ی دیلود یا فاز جدید رو تنظیم کن.",
                reply_markup=keyboard
            )
        except Exception: pass
