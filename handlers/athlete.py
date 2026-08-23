from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from database import set_coach_for_athlete, get_user, get_athlete_active_plan

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
    user = get_user(callback_query.from_user.id)
    
    # ساخت مستقیم منوی اصلی به صورت شیشه‌ای
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 شروع تمرین امروز", callback_data="start_workout_menu")],
        [InlineKeyboardButton(text="📝 ساخت/ویرایش برنامه من", callback_data="create_solo_plan")],
        [InlineKeyboardButton(text="📈 مشاهده پیشرفت من", callback_data="my_progress_menu")]
    ])
    
    text = (
        f"🔥 **ایول به اراده‌ت!**\n\n"
        f"سلام {user['name']} عزیز! 💪\n"
        f"به پنل کاربری خودت خوش اومدی. از اینجا می‌تونی همه کارهات رو مدیریت کنی:"
    )
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


# --- منوی اصلی ورزشکار (شیشه‌ای) با دستور menu/ ---
@athlete_router.message(Command("menu"))
async def athlete_main_menu(message: types.Message):
    user = get_user(message.from_user.id)
    if not user:
        return
        
    # یک ترفند ریز برای پاک کردن کیبوردهای قدیمی (اگه گیر کرده باشن)
    msg = await message.answer("🔄", reply_markup=ReplyKeyboardRemove())
    await msg.delete()
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 شروع تمرین امروز", callback_data="start_workout_menu")],
        [InlineKeyboardButton(text="📝 ساخت/ویرایش برنامه من", callback_data="create_solo_plan")],
        [InlineKeyboardButton(text="👨‍🏫 اطلاعات مربی من", callback_data="my_coach_menu")],
        [InlineKeyboardButton(text="📈 مشاهده پیشرفت", callback_data="my_progress_menu")]
    ])
    
    await message.answer(
        f"سلام {user['name']} عزیز! 💪\nبه پنل کاربری خودت خوش اومدی. چه کاری برات انجام بدم؟",
        reply_markup=keyboard
    )

# --- مدیریت کلیک روی دکمه‌های پنل ---
@athlete_router.callback_query(F.data == "start_workout_menu")
async def handle_start_workout_btn(callback_query: types.CallbackQuery):
    plan = get_athlete_active_plan(callback_query.from_user.id)
    if not plan:
        await callback_query.answer("❌ تو هنوز هیچ برنامه فعالی نداری! اول یه برنامه بساز.", show_alert=True)
        return
    
    await callback_query.answer()
    # اگر برنامه داشت، راهنماییش می‌کنیم به کامند شروع تمرین
    await callback_query.message.answer("برای شروع تمرینت، روی دستور 👉 /start_workout کلیک کن.")

@athlete_router.callback_query(F.data == "create_solo_plan")
async def handle_create_solo_plan(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("🛠 برای ساخت برنامه جدید، روی دستور 👉 /newplan کلیک کن تا قدم به قدم با هم بسازیمش.")
    
@athlete_router.callback_query(F.data == "my_progress_menu")
async def handle_progress_btn(callback_query: types.CallbackQuery):
    await callback_query.answer("این بخش به زودی آماده میشه! 🚧", show_alert=True)
    
@athlete_router.callback_query(F.data == "my_coach_menu")
async def handle_coach_btn(callback_query: types.CallbackQuery):
    user = get_user(callback_query.from_user.id)
    if user and user.get('coach_id'):
        coach = get_user(user['coach_id'])
        if coach:
            await callback_query.answer(f"مربی شما: {coach['name']}", show_alert=True)
            return
    await callback_query.answer("❌ شما هنوز مربی انتخاب نکردید.", show_alert=True)

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
