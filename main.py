import asyncio
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import get_athlete_active_plan, get_exercises_for_plan, log_exercise_set

workout_router = Router()

class WorkoutSession(StatesGroup):
    waiting_for_performance = State()

# یک کیبورد مخصوص زمان تمرین
def get_workout_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⏹ پایان تمرین")]],
        resize_keyboard=True
    )

# --- استارت تمرین با کلیک روی دکمه منوی اصلی ---
@workout_router.message(F.text == "🚀 شروع تمرین امروز")
async def start_workout(message: types.Message, state: FSMContext):
    plan = get_athlete_active_plan(message.from_user.id)
    
    if not plan:
        return await message.answer("❌ شما در حال حاضر هیچ برنامه فعالی ندارید.\nاول از منوی اصلی یک برنامه بسازید.")
        
    exercises = get_exercises_for_plan(plan['id'])
    if not exercises:
        return await message.answer("❌ برنامه‌ی شما هنوز هیچ حرکتی نداره! از منو دکمه 'اضافه کردن حرکت' رو بزن.")
        
    # ذخیره لیست حرکات و وضعیت فعلی در State
    await state.update_data(
        exercises=exercises,
        current_ex_index=0,
        current_set=1
    )
    
    await message.answer("🔥 تمرین امروز استارت خورد! پرقدرت برو جلو.", reply_markup=get_workout_keyboard())
    await send_next_exercise_or_set(message, state)


async def send_next_exercise_or_set(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data: return # در صورتی که State پاک شده باشه
    
    exercises = data['exercises']
    current_ex_index = data['current_ex_index']
    current_set = data['current_set']
    
    # اگر تمام حرکات تمام شده باشد
    if current_ex_index >= len(exercises):
        from handlers.athlete import get_athlete_main_keyboard
        await message.answer("🎉 خسته نباشی قهرمان! تمرین امروزت با موفقیت تموم شد و ثبت شد.", reply_markup=get_athlete_main_keyboard())
        await state.clear()
        return
        
    current_ex_data = exercises[current_ex_index]
    ex_info = current_ex_data.get('exercise_id', {}) 
    ex_name = ex_info.get('name', 'حرکت نامشخص')
    total_sets = current_ex_data['sets']
    target_reps = current_ex_data['reps']
    
    text = (
        f"🏋️‍♂️ **{ex_name}**\n"
        f"📊 ست {current_set} از {total_sets}\n"
        f"🔄 تکرار هدف: {target_reps}\n\n"
        f"👈 عملکرد این ست رو به این شکل برام بنویس:\n"
        f"`وزنه-تکرار` (مثلاً: `50-10`)"
    )
    
    # اگه حرکت ویدیو داشت بفرست
    media_id = ex_info.get('media_file_id')
    if media_id:
        await message.answer_video(video=media_id, caption=text, parse_mode="Markdown", reply_markup=get_workout_keyboard())
    else:
        await message.answer(text, parse_mode="Markdown", reply_markup=get_workout_keyboard())
        
    await state.set_state(WorkoutSession.waiting_for_performance)


# --- دریافت عملکرد ورزشکار در هر ست ---
@workout_router.message(WorkoutSession.waiting_for_performance)
async def process_performance(message: types.Message, state: FSMContext):
    # اگه دکمه پایان رو زد
    if message.text == "⏹ پایان تمرین":
        from handlers.athlete import get_athlete_main_keyboard
        await state.clear()
        return await message.answer("🛑 تمرین متوقف شد. خسته نباشی!", reply_markup=get_athlete_main_keyboard())
        
    # اعتبارسنجی ورودی کاربر (مثلاً 50-10)
    try:
        parts = message.text.replace(' ', '').split('-')
        if len(parts) != 2: raise ValueError
        weight = float(parts[0])
        reps = int(parts[1])
    except ValueError:
        return await message.answer("❌ فرمت اشتباهه!\nلطفاً فقط با فرمت `وزنه-تکرار` بفرست. مثلاً بنویس: `50-10`")
        
    data = await state.get_data()
    exercises = data['exercises']
    current_ex_index = data['current_ex_index']
    current_set = data['current_set']
    
    current_ex_data = exercises[current_ex_index]
    ex_info = current_ex_data.get('exercise_id', {})
    ex_name = ex_info.get('name', 'حرکت نامشخص')
    rest_time = current_ex_data.get('rest_time', 60)
    
    # ثبت در دیتابیس
    log_exercise_set(
        athlete_id=message.from_user.id,
        exercise_name=ex_name,
        set_number=current_set,
        reps_done=reps,
        weight_used=weight
    )
    
    total_sets = current_ex_data['sets']
    
    # به‌روزرسانی ست و حرکت بعدی
    if current_set < total_sets:
        await state.update_data(current_set=current_set + 1)
    else:
        await state.update_data(current_ex_index=current_ex_index + 1, current_set=1)

    # تایمر استراحت در پس‌زمینه
    await message.answer(f"✅ ثبت شد!\n⏱ حالا **{rest_time} ثانیه** استراحت کن...")
    
    async def rest_timer():
        await asyncio.sleep(rest_time)
        # چک میکنیم کاربر وسط استراحت تمرین رو قطع نکرده باشه
        current_state = await state.get_state()
        if current_state:
            await message.answer("🔔 **وقت استراحت تمومه!** بریم سراغ ادامه...", reply_markup=get_workout_keyboard())
            await send_next_exercise_or_set(message, state)
            
    asyncio.create_task(rest_timer())
