from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext # این خط برای مدیریت فرم اضافه شد
from database import get_user, create_user
from handlers.assessment import start_assessment

auth_router = Router()

@auth_router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext): # متغیر state اینجا اضافه شد
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
        create_user(telegram_id=user_id, name=message.from_user.full_name)
        # فراخوانی شروع فرم ارزیابی برای کاربر جدید
        await start_assessment(message, state)
