from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import set_coach_for_athlete, get_user

athlete_router = Router()

# --- واکنش به دکمه‌های شیشه‌ای پایان فرم ثبت‌نام ---
@athlete_router.callback_query(F.data == "choose_coach_flow")
async def ask_for_coach_id(callback_query: types.CallbackQuery):
    text = (
        "🔍 **انتخاب مربی**\n\n"
        "برای اتصال به مربیت، کافیه آیدی عددیِ مربیت رو با دستور زیر برام بفرستی:\n\n"
        "👉 `/setcoach 123456789`\n\n"
        "*(اگه آیدی مربیت رو نداری، ازش بخواه که بهت بده)*"
    )
    await callback_query.message.edit_text(text, parse_mode="Markdown")

@athlete_router.callback_query(F.data == "solo_training_flow")
async def set_solo_training(callback_query: types.CallbackQuery):
    text = (
        "🔥 **ایول به اراده‌ت!**\n\n"
        "تو می‌تونی برنامه‌های خودت رو بچینی، وزنه و تکرارهات رو لاگ کنی و از تایمر هوشمند بات استفاده کنی.\n"
        "برای باز کردن منوی اصلی، دستور /menu رو بزن."
    )
    await callback_query.message.edit_text(text, parse_mode="Markdown")

# --- منوی اصلی ورزشکار (شیشه‌ای) ---
@athlete_router.message(Command("menu"))
async def athlete_main_menu(message: types.Message):
    user = get_user(message.from_user.id)
    if not user:
        return
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 شروع تمرین امروز", callback_data="start_workout_menu")],
        [InlineKeyboardButton(text="👨‍🏫 اطلاعات مربی من", callback_data="my_coach_menu")],
        [InlineKeyboardButton(text="📈 مشاهده پیشرفت من", callback_data="my_progress_menu")]
    ])
    
    await message.answer(
        f"سلام {user['name']} عزیز! 💪\nبه پنل کاربری خودت خوش اومدی. چه کاری برات انجام بدم؟",
        reply_markup=keyboard
    )

# --- دستور تنظیم مربی ---
@athlete_router.message(Command("setcoach"))
async def choose_coach(message: types.Message):
    try:
        coach_id = int(message.text.split()[1])
        coach = get_user(coach_id)
        
        if not coach:
            await message.answer("❌ مربی با این آیدی پیدا نشد! مطمئنی عدد رو درست زدی؟")
            return
            
        if coach.get("role") not in ["coach", "admin"]:
            await message.answer("❌ کاربری که وارد کردی مربی نیست!")
            return
            
        set_coach_for_athlete(message.from_user.id, coach_id)
        await message.answer(f"✅ عالیه! تو الان شاگرد استاد **{coach['name']}** هستی. 🏋️‍♂️")
        
        await message.bot.send_message(chat_id=coach_id, text=f"🎉 تبریک! ورزشکار جدیدی به اسم **{message.from_user.full_name}** تو رو به عنوان مربی انتخاب کرد.")
        
    except (IndexError, ValueError):
        await message.answer("❌ فرمت اشتباهه رفیق.\nدرستش اینه: `/setcoach 12345678`")
