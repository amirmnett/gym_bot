from aiogram import Router, F, types
from aiogram.filters import Command
import config
from database import update_user_role, get_all_users

admin_router = Router()

# فیلتر برای اینکه فقط ادمین بتونه این دستورات رو اجرا کنه
is_admin = F.from_user.id == config.ADMIN_USER_ID

@admin_router.message(Command("admin"), is_admin)
async def admin_panel(message: types.Message):
    text = """👑 **پنل مدیریت کل بات** 👑

دستورات موجود:
🔸 `/promote <User_ID>` - ارتقای کاربر به مربی
🔸 `/demote <User_ID>` - تنزل مربی به ورزشکار
🔸 `/broadcast <متن>` - ارسال پیام سراسری به همه
🔸 `/stats` - آمار کلی بات
"""
    await message.answer(text, parse_mode="Markdown")

@admin_router.message(Command("promote"), is_admin)
async def promote_user(message: types.Message):
    try:
        user_id = int(message.text.split()[1])
        update_user_role(user_id, "coach")
        await message.answer(f"✅ کاربر {user_id} با موفقیت به **مربی** ارتقا یافت.")
    except (IndexError, ValueError):
        await message.answer("❌ فرمت اشتباه است. مثال:\n`/promote 123456789`")

@admin_router.message(Command("demote"), is_admin)
async def demote_user(message: types.Message):
    try:
        user_id = int(message.text.split()[1])
        update_user_role(user_id, "athlete")
        await message.answer(f"✅ کاربر {user_id} به **ورزشکار** تغییر نقش داد.")
    except (IndexError, ValueError):
        await message.answer("❌ فرمت اشتباه است. مثال:\n`/demote 123456789`")

@admin_router.message(Command("broadcast"), is_admin)
async def broadcast_message(message: types.Message):
    text_to_send = message.text.replace("/broadcast", "").strip()
    if not text_to_send:
        await message.answer("❌ لطفاً متن پیام را بعد از دستور بنویسید.\nمثال: `/broadcast سلام بچه‌ها!`")
        return

    users = get_all_users()
    count = 0
    await message.answer("⏳ در حال ارسال پیام...")
    
    for user in users:
        try:
            await message.bot.send_message(chat_id=user['telegram_id'], text=f"📢 **پیام مدیریت:**\n\n{text_to_send}", parse_mode="Markdown")
            count += 1
        except Exception:
            pass # کاربر بات را بلاک کرده است
            
    await message.answer(f"✅ پیام سراسری به {count} نفر ارسال شد.")
