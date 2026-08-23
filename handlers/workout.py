import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database import get_athlete_active_plan, get_exercises_for_plan, log_exercise_set

workout_router = Router()

class WorkoutSession(StatesGroup):
    waiting_for_performance = State() # منتظر دریافت وزنه و تکرار از ورزشکار

@workout_router.message(Command("start_workout"))
async def start_workout(message: types.Message, state: FSMContext):
    athlete_id = message.from_user.id
    plan = get_athlete_active_plan(athlete_id)
    
    if not plan:
        await message.answer("❌ شما در حال حاضر هیچ برنامه فعالی ندارید.")
        return
        
    exercises = get_exercises_for_plan(plan['id'])
    if not exercises:
        await message.answer("❌ برنامه‌ی شما هنوز حرکتی نداره. به مربیتون اطلاع بدید.")
        return
        
    # ذخیره لیست حرکات و وضعیت فعلی در State
    await state.update_data(
        exercises=exercises,
        current_ex_index=0,
        current_set=1
    )
    
    await message.answer("🔥 تمرین رو شروع می‌کنیم! پرقدرت برو جلو.")
    await send_next_exercise_or_set(message, state)


async def send_next_exercise_or_set(message: types.Message, state: FSMContext):
    data = await state.get_data()
    exercises = data['exercises']
    current_ex_index = data['current_ex_index']
    current_set = data['current_set']
    
    # اگر تمام حرکات تمام شده باشد
    if current_ex_index >= len(exercises):
        await message.answer("🎉 خسته نباشی قهرمان! تمرین امروزت تموم شد.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
        
    current_ex_data = exercises[current_ex_index]
    # به دلیل Join در سوپابیس، اطلاعات حرکت داخل exercise_id قرار میگیره (اگر اسم ستون فرق داره اصلاح کن)
    ex_info = current_ex_data.get('exercise_id', {}) 
    ex_name = ex_info.get('name', 'حرکت نامشخص')
    total_sets = current_ex_data['sets']
    target_reps = current_ex_data['reps']
    
    # پیام اعلام حرکت و ست
    text = (
        f"🏋️‍♂️ **{ex_name}**\n"
        f"📊 ست {current_set} از {total_sets}\n"
        f"🔄 تکرار هدف: {target_reps}\n\n"
        f"👈 بعد از انجام این ست، عملکردت رو به این شکل بنویس:\n"
        f"`وزنه-تکرار` (مثلاً اگه با وزنه 50 کیلویی 10 تا زدی بنویس: `50-10`)"
    )
    
    # اگه ویدیو داشت بفرست
    media_id = ex_info.get('media_file_id')
    if media_id:
        await message.answer_video(video=media_id, caption=text, parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")
        
    await state.set_state(WorkoutSession.waiting_for_performance)


@workout_router.message(WorkoutSession.waiting_for_performance)
async def process_performance(message: types.Message, state: FSMContext):
    # اعتبارسنجی ورودی کاربر (مثلاً 50-10)
    try:
        weight_str, reps_str = message.text.split('-')
        weight = float(weight_str.strip())
        reps = int(reps_str.strip())
    except ValueError:
        await message.answer("❌ فرمت اشتباهه! لطفاً فقط با فرمت `وزنه-تکرار` بفرست. مثلاً `50-10`")
        return
        
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
        next_step_msg = f"ست بعدی همون حرکت ({ex_name})"
    else:
        await state.update_data(current_ex_index=current_ex_index + 1, current_set=1)
        next_step_msg = "حرکت بعدی"

    # تایمر استراحت (بدون بلاک کردن ربات)
    await message.answer(f"✅ ثبت شد!\n⏱ حالا **{rest_time} ثانیه** استراحت کن...")
    
    # ایجاد یک تسک پس‌زمینه برای استراحت
    async def rest_timer():
        await asyncio.sleep(rest_time)
        await message.answer("🔔 **وقت استراحت تمومه!** بریم سراغ ادامه...")
        await send_next_exercise_or_set(message, state)
        
    asyncio.create_task(rest_timer())
