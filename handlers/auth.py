from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import get_user, create_user
from handlers.assessment import start_assessment

auth_router = Router()

@auth_router.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if user:
        if user['role'] in ['coach', 'admin']:
            # ورود به پنل مربی
            from handlers.coach import get_coach_main_keyboard
            await message.answer(
                f"سلام استاد {user['name']}! 👨‍🏫\nبه پنل مدیریت مربیان خوش آمدید.",
                reply_markup=get_coach_main_keyboard()
            )
        else:
            # ورود به پنل ورزشکار
            from handlers.athlete import get_athlete_main_keyboard
            await message.answer(
                f"سلام {user['name']} عزیز! به باشگاه خوش اومدی. 💪\nاز منوی پایین می‌تونی تمرینت رو مدیریت کنی:",
                reply_markup=get_athlete_main_keyboard()
            )
    else:
        # کاربر جدید
        create_user(user_id, message.from_user.full_name)
        await start_assessment(message, state)
