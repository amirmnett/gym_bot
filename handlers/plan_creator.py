from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from database import create_workout_plan, get_user

plan_router = Router()

class PlanCreation(StatesGroup):
    athlete_id = State()
    title = State()
    duration = State()

# این هندلر دکمه‌ای که در پنل مربی ساخته بودیم را می‌گیرد
@plan_router.callback_query(F.data.startswith("newplan_"))
async def start_plan_creation(callback_query: types.CallbackQuery, state: FSMContext):
    athlete_id = int(callback_query.data.split('_')[1])
    athlete = get_user(athlete_id)
    
    if not athlete:
        await callback_query.answer("❌ ورزشکار پیدا نشد!", show_alert=True)
        return

    await state.update_data(athlete_id=athlete_id)
    await state.set_state(PlanCreation.title)
    
    await callback_query.message.answer(
        f"📝 در حال نوشتن برنامه برای **{athlete['name']}** هستید.\n\n"
        "نام این دوره تمرینی چیست؟ (مثلاً: فاز اول چربی‌سوزی - بهاره)",
        parse_mode="Markdown"
    )
    await callback_query.answer()

@plan_router.message(PlanCreation.title)
async def process_plan_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(PlanCreation.duration)
    await message.answer("مدت زمان این برنامه چند روز است؟ (مثلاً بنویسید 40)")

@plan_router.message(PlanCreation.duration)
async def process_plan_duration(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ لطفاً فقط عدد وارد کنید (مثلاً 40):")
        return
        
    duration = int(message.text)
    data = await state.get_data()
    
    # ساخت برنامه در دیتابیس
    plan = create_workout_plan(
        coach_id=message.from_user.id,
        athlete_id=data['athlete_id'],
        title=data['title'],
        duration_days=duration
    )
    
    await state.clear()
    
    if plan:
        await message.answer(
            f"✅ برنامه **{data['title']}** با موفقیت ایجاد شد.\n\n"
            "🔍 حالا برای اضافه کردن حرکات، کافیه اسم بات رو به همراه اسم حرکت تایپ کنی تا جستجو باز بشه!\n"
            "مثال: `@YourBotUsername پرس سینه`",
            parse_mode="Markdown"
        )
        # اطلاع به شاگرد
        await message.bot.send_message(
            chat_id=data['athlete_id'],
            text=f"🎉 ورزشکار عزیز، مربی برنامه‌ی جدیدت به نام **{data['title']}** را برای {duration} روز آینده ساخت!"
        )
    else:
        await message.answer("❌ خطایی در ساخت برنامه رخ داد.")
