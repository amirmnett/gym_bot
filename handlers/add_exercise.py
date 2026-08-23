from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_latest_plan_by_coach, add_exercise_to_plan

exercise_router = Router()

class ExerciseDetails(StatesGroup):
    day_number = State()
    sets = State()
    reps = State()
    rest_time = State()

@exercise_router.message(Command("add_exercise"))
async def start_adding_exercise(message: types.Message, state: FSMContext):
    try:
        exercise_id = message.text.split()[1]
    except IndexError:
        return
        
    # پیدا کردن برنامه‌ای که مربی در حال ویرایش آن است
    plan = get_latest_plan_by_coach(message.from_user.id)
    if not plan:
        await message.answer("❌ شما هیچ برنامه فعالی برای ویرایش ندارید. اول یک برنامه جدید بسازید.")
        return

    # ذخیره موقت آیدی حرکت و آیدی برنامه در State
    await state.update_data(exercise_id=exercise_id, plan_id=plan['id'])
    
    await state.set_state(ExerciseDetails.day_number)
    await message.answer("📅 این حرکت برای **روز چندم** برنامه است؟ (فقط عدد وارد کنید، مثلاً 1 برای روز اول)")

@exercise_router.message(ExerciseDetails.day_number)
async def process_day_number(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ لطفاً فقط عدد وارد کنید:")
        return
    await state.update_data(day_number=int(message.text))
    await state.set_state(ExerciseDetails.sets)
    await message.answer("🔢 تعداد **ست‌ها** چقدر است؟ (مثلاً 4)")

@exercise_router.message(ExerciseDetails.sets)
async def process_sets(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ لطفاً فقط عدد وارد کنید:")
        return
    await state.update_data(sets=int(message.text))
    await state.set_state(ExerciseDetails.reps)
    await message.answer("🔄 تعداد **تکرارها** چقدر است؟\n(می‌توانید بنویسید '12' یا '12-10-8' یا 'تا ناتوانی')")

@exercise_router.message(ExerciseDetails.reps)
async def process_reps(message: types.Message, state: FSMContext):
    await state.update_data(reps=message.text)
    await state.set_state(ExerciseDetails.rest_time)
    await message.answer("⏱ زمان **استراحت بین ست‌ها** چقدر باشد؟ (به ثانیه، مثلاً 60)")

@exercise_router.message(ExerciseDetails.rest_time)
async def process_rest_time(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ لطفاً فقط عدد (به ثانیه) وارد کنید:")
        return
        
    data = await state.get_data()
    rest_time = int(message.text)
    
    # ذخیره نهایی در دیتابیس
    add_exercise_to_plan(
        plan_id=data['plan_id'],
        day_number=data['day_number'],
        exercise_id=data['exercise_id'],
        sets=data['sets'],
        reps=data['reps'],
        rest_time=rest_time
    )
    
    await state.clear()
    await message.answer("✅ حرکت با موفقیت به برنامه اضافه شد!\n\nبرای اضافه کردن حرکت بعدی، دوباره از `@نام_بات` استفاده کنید.")
