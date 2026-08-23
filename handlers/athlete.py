from aiogram import F, Router, types
from aiogram.filters import Command
from database import set_coach_for_athlete, get_user

athlete_router = Router()

@athlete_router.message(Command("setcoach"))
async def choose_coach(message: types.Message):
    try:
        coach_id = int(message.text.split()[1])
        # بررسی اینکه آیا این آیدی واقعا یک مربی است یا نه
        coach = get_user(coach_id)
        
        if not coach:
            await message.answer("❌ کاربری با این آیدی یافت نشد.")
            return
            
        if coach.get("role") != "coach" and coach.get("role") != "admin":
            await message.answer("❌ کاربری که وارد کردید مربی نیست!")
            return
            
        set_coach_for_athlete(message.from_user.id, coach_id)
        await message.answer(f"✅ با موفقیت مربی شما به استاد **{coach['name']}** تغییر یافت.")
        
        # ارسال پیام به مربی که یک شاگرد جدید داره
        await message.bot.send_message(chat_id=coach_id, text=f"🎉 تبریک! ورزشکار {message.from_user.full_name} شما را به عنوان مربی انتخاب کرد.")
        
    except (IndexError, ValueError):
        await message.answer("❌ فرمت اشتباه است. لطفاً آیدی عددی مربی را روبروی دستور بنویسید.\nمثال: `/setcoach 12345678`")
