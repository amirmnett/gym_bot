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
        # اگر کاربر قبلاً ثبت‌نام کرده، منوی اصلی پایین صفحه رو براش باز می‌کنیم
        from handlers.athlete import get_athlete_main_keyboard
        await message.answer(
            f"سلام {user['name']} عزیز! به باشگاه خوش اومدی. 💪\nاز منوی پایین می‌تونی تمرینت رو مدیریت کنی:",
            reply_markup=get_athlete_main_keyboard()
        )
    else:
        # اگر کاربر جدیده، میره برای فرم ثبت‌نام
        create_user(user_id, message.from_user.full_name)
        await start_assessment(message, state)
