from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import set_coach_for_athlete, get_user, get_athlete_active_plan

athlete_router = Router()

# ساخت کیبورد دائمی پایین صفحه
def get_athlete_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 شروع تمرین امروز")],
            [KeyboardButton(text="📝 ساخت/ویرایش برنامه من")],
            [KeyboardButton(text="👨‍🏫 اطلاعات مربی من"), KeyboardButton(text="📈 پیشرفت من")]
        ],
        resize_keyboard=True,
        is_persistent=True # باعث میشه کیبورد همیشه باز بمونه
    )

# --- واکنش به دکمه‌های پایین صفحه ---

@athlete_router.message(F.text == "🚀 شروع تمرین امروز")
async def handle_start_workout_btn(message: types.Message):
    plan = get_athlete_active_plan(message.from_user.id)
    if not plan:
        await message.answer("❌ تو هنوز هیچ برنامه فعالی نداری!\nاول از منوی پایین روی «📝 ساخت/ویرایش برنامه من» کلیک کن تا برنامه‌ت رو بچینیم.")
        return
    
    # فعلا با دستور استارت تمرین رو فراخوانی میکنیم تا در آپدیت بعدی اینم خودکار بشه
    await message.answer("🔥 همه‌چیز آماده‌ست! برای شروع تمرینت روی این دستور کلیک کن:\n👉 /start_workout")

@athlete_router.message(F.text == "📝 ساخت/ویرایش برنامه من")
async def handle_create_solo_plan(message: types.Message):
    # اینجا در مرحله بعد یک فرم تعاملی با دکمه (بدون نیاز به نوشتن دستور) باز می‌کنیم
    text = (
        "🛠 **بخش ساخت برنامه تعاملی**\n\n"
        "این بخش در حال طراحی است تا بتوانی بدون نیاز به نوشتن هیچ کدی و فقط با زدن دکمه‌ها، حرکاتت را از دیتابیس انتخاب کنی و برنامه‌ات را بسازی. 🚧\n"
    )
    await message.answer(text, parse_mode="Markdown")
    
@athlete_router.message(F.text == "👨‍🏫 اطلاعات مربی من")
async def handle_my_coach(message: types.Message):
    user = get_user(message.from_user.id)
    if user and user.get('coach_id'):
        coach = get_user(user['coach_id'])
        if coach:
            await message.answer(f"👨‍🏫 مربی شما: **{coach['name']}**", parse_mode="Markdown")
            return
            
    await message.answer(
        "❌ تو در حال حاضر به تنهایی تمرین می‌کنی و مربی نداری.\n\n"
        "اگر می‌خواهی مربی داشته باشی، فعلاً می‌توانی آیدی او را به این شکل بفرستی:\n`/setcoach 123456789`",
        parse_mode="Markdown"
    )

@athlete_router.message(F.text == "📈 پیشرفت من")
async def handle_progress(message: types.Message):
    await message.answer("این بخش به زودی آماده میشه! 🚧")

# --- تنظیم مربی (در آینده اینم دکمه‌ای می‌کنیم) ---
@athlete_router.message(Command("setcoach"))
async def choose_coach(message: types.Message):
    try:
        coach_id = int(message.text.split()[1])
        coach = get_user(coach_id)
        if not coach or coach.get("role") not in ["coach", "admin"]:
            await message.answer("❌ مربی با این آیدی پیدا نشد یا شخص مورد نظر مربی نیست!")
            return
            
        set_coach_for_athlete(message.from_user.id, coach_id)
        await message.answer(f"✅ عالیه! تو الان شاگرد استاد **{coach['name']}** هستی. 🏋️‍♂️")
        await message.bot.send_message(chat_id=coach_id, text=f"🎉 تبریک! ورزشکار جدیدی به اسم **{message.from_user.full_name}** تو رو به عنوان مربی انتخاب کرد.")
    except (IndexError, ValueError):
        await message.answer("❌ فرمت اشتباهه.")
