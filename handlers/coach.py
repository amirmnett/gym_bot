from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_user, get_coach_athletes

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
