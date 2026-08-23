from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import update_exercise_media

media_router = Router()

class MediaUpload(StatesGroup):
    waiting_for_exercise_id = State()
    waiting_for_video = State()

@media_router.message(Command("addmedia"))
async def start_add_media(message: types.Message, state: FSMContext):
    # برای امنیت بیشتر، می‌تونی چک کنی که فقط ادمین یا مربی بتونه این دستور رو بزنه
    await state.set_state(MediaUpload.waiting_for_exercise_id)
    text = (
        "🎥 **اضافه کردن ویدیو/گیف به حرکت**\n\n"
        "ابتدا **آیدی (ID)** حرکت را بفرستید.\n\n"
        "💡 *راهنمایی:* می‌توانید اسم حرکت را با `@نام_بات` سرچ کنید، پیامی که شامل `/add_exercise و آیدی` است را کپی کرده و فقط بخش آیدی را اینجا بفرستید."
    )
    await message.answer(text, parse_mode="Markdown")

@media_router.message(MediaUpload.waiting_for_exercise_id, F.text)
async def process_exercise_id(message: types.Message, state: FSMContext):
    # دریافت آیدی حرکت
    await state.update_data(exercise_id=message.text.strip())
    await state.set_state(MediaUpload.waiting_for_video)
    await message.answer("✅ آیدی دریافت شد. حالا لطفاً **ویدیو** یا **گیف (Animation)** حرکت را ارسال کنید:")

@media_router.message(MediaUpload.waiting_for_video, F.video | F.animation)
async def process_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    exercise_id = data['exercise_id']
    
    # تلگرام برای ویدیو و گیف دو آبجکت متفاوت داره، چک می‌کنیم کدوم فرستاده شده
    if message.video:
        file_id = message.video.file_id
    elif message.animation:
        file_id = message.animation.file_id
    else:
        await message.answer("❌ فرمت فایل پشتیبانی نمی‌شود. لطفاً فقط ویدیو یا فایل گیف بفرستید.")
        return

    try:
        # ذخیره در سوپابیس
        update_exercise_media(exercise_id, file_id)
        await message.answer("🎉 ویدیو با موفقیت به حرکت متصل شد!\n\nاز این به بعد وقتی ورزشکار تمرینش رو شروع کنه، این ویدیو رو بالای ست‌های این حرکت می‌بینه.")
    except Exception as e:
        await message.answer(f"❌ خطایی در ثبت رخ داد (احتمالاً آیدی حرکت اشتباه است).\nمتن خطا: {e}")
        
    await state.clear()
