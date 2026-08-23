from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_user, get_coach_athletes
from collections import defaultdict
from aiogram.types import BufferedInputFile
from utils.charts import generate_progress_chart
from database import get_athlete_logs

coach_router = Router()

@coach_router.message(Command("coach"))
async def coach_panel(message: types.Message):
    user = get_user(message.from_user.id)
    
    if not user or user.get("role") != "coach":
        await message.answer("❌ شما به این بخش دسترسی ندارید.")
        return

    athletes = get_coach_athletes(message.from_user.id)
    
    if not athletes:
        await message.answer("شما هنوز هیچ شاگردی ندارید.")
        return

    # ساخت دکمه شیشه‌ای (Inline) برای لیست شاگردان
    buttons = []
    for ath in athletes:
        btn = InlineKeyboardButton(text=ath['name'], callback_data=f"athlete_{ath['telegram_id']}")
        buttons.append([btn])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("👥 **لیست شاگردان شما:**\nبرای مشاهده اطلاعات، برنامه‌دهی یا نمودارها، روی نام شاگرد کلیک کنید.", reply_markup=keyboard)

@coach_router.callback_query(lambda c: c.data and c.data.startswith('athlete_'))
async def athlete_details(callback_query: types.CallbackQuery):
    athlete_id = int(callback_query.data.split('_')[1])
    
    # دکمه‌های مدیریتی برای این شاگرد خاص
    buttons = [
        [InlineKeyboardButton(text="📋 فرم ارزیابی اولیه", callback_data=f"assess_{athlete_id}")],
        [InlineKeyboardButton(text="✍️ دادن برنامه جدید", callback_data=f"newplan_{athlete_id}")],
        [InlineKeyboardButton(text="📈 نمودار پیشرفت کلی", callback_data=f"chart_all_{athlete_id}")],
        [InlineKeyboardButton(text="🦵 نمودار پیشرفت پا (Legs)", callback_data=f"chart_legs_{athlete_id}")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(f"تنظیمات برای شاگرد با آیدی: {athlete_id}\nلطفاً یک گزینه را انتخاب کنید:", reply_markup=keyboard)
@coach_router.callback_query(lambda c: c.data and c.data.startswith('chart_all_'))
async def send_total_progress_chart(callback_query: types.CallbackQuery):
    athlete_id = int(callback_query.data.split('_')[2])
    logs = get_athlete_logs(athlete_id)
    
    if not logs:
        await callback_query.answer("❌ این ورزشکار هنوز تمرینی ثبت نکرده است.", show_alert=True)
        return
        
    await callback_query.message.answer("⏳ در حال تحلیل داده‌ها و رسم نمودار...")
    
    # محاسبه حجم کل تمرین (وزنه × تکرار) به تفکیک روز
    volume_by_date = defaultdict(float)
    for log in logs:
        date_str = log['created_at'].split('T')[0] # جدا کردن بخش تاریخ
        volume = log['reps_done'] * log['weight_used']
        volume_by_date[date_str] += volume
        
    sorted_dates = sorted(volume_by_date.keys())
    volumes = [volume_by_date[d] for d in sorted_dates]
    
    if len(sorted_dates) < 2:
        await callback_query.message.answer("⚠️ برای رسم نمودار پیشرفت، به حداقل اطلاعات ۲ روز تمرین نیاز داریم.")
        await callback_query.answer()
        return
        
    # تولید عکس نمودار
    buf = generate_progress_chart(sorted_dates, volumes, "Total Training Volume Progress (kg)")
    photo = BufferedInputFile(buf.getvalue(), filename="total_chart.png")
    
    await callback_query.message.answer_photo(
        photo=photo, 
        caption="📈 **نمودار پیشرفت کلی**\nاین نمودار مجموع حجم تمرینی (وزنه × تکرار) شاگرد را در روزهای مختلف نشان می‌دهد."
    )
    await callback_query.answer()


@coach_router.callback_query(lambda c: c.data and c.data.startswith('chart_legs_'))
async def send_legs_progress_chart(callback_query: types.CallbackQuery):
    athlete_id = int(callback_query.data.split('_')[2])
    logs = get_athlete_logs(athlete_id)
    
    if not logs:
        await callback_query.answer("❌ این ورزشکار هنوز تمرینی ثبت نکرده است.", show_alert=True)
        return
        
    # فیلتر کردن حرکاتی که اسمشون شامل کلمات مربوط به پا است
    leg_keywords = ["پا", "اسکوات", "پرس", "ساق", "squat", "leg", "press"]
    leg_logs = [log for log in logs if any(k in log['exercise_name'].lower() for k in leg_keywords)]
    
    if not leg_logs:
        await callback_query.answer("❌ این شاگرد هنوز دیتایی برای تمرینات پا ثبت نکرده است.", show_alert=True)
        return
        
    await callback_query.message.answer("⏳ در حال رسم نمودار تمرینات پا...")
    
    volume_by_date = defaultdict(float)
    for log in leg_logs:
        date_str = log['created_at'].split('T')[0]
        volume = log['reps_done'] * log['weight_used']
        volume_by_date[date_str] += volume
        
    sorted_dates = sorted(volume_by_date.keys())
    volumes = [volume_by_date[d] for d in sorted_dates]
    
    if len(sorted_dates) < 2:
        await callback_query.message.answer("⚠️ برای رسم نمودار تمرینات پا، به حداقل اطلاعات ۲ روز تمرین نیاز داریم.")
        await callback_query.answer()
        return
        
    buf = generate_progress_chart(sorted_dates, volumes, "Legs Training Volume Progress (kg)")
    photo = BufferedInputFile(buf.getvalue(), filename="legs_chart.png")
    
    await callback_query.message.answer_photo(
        photo=photo, 
        caption="🦵 **نمودار پیشرفت عضلات پا**\nروند تغییرات حجم تمرینی این شاگرد در حرکات پایین‌تنه."
    )
    await callback_query.answer()
