from aiogram import Router, types
from aiogram.filters import CommandStart
from database import get_user, create_user

auth_router = Router()

@auth_router.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if user:
        role = user.get("role")
        if role == "admin":
            await message.answer("سلام قربان! به پنل مدیریت خوش آمدید.")
        elif role == "coach":
            await message.answer(f"سلام مربی {user['name']}! آماده‌ای به شاگردات برنامه بدی؟")
        else:
            await message.answer(f"سلام {user['name']} عزیز! به بات باشگاه خوش اومدی. از منو می‌تونی تمرینت رو شروع کنی.")
    else:
        # ثبت نام کاربر جدید
        create_user(telegram_id=user_id, name=message.from_user.full_name)
        await message.answer("سلام! به نظر میاد تازه وارد بات شدی. به عنوان 'ورزشکار' ثبت‌نام شدی.\nبرای دریافت برنامه، لطفاً ابتدا به سوالات ارزیابی ما پاسخ بده... (به زودی)")
