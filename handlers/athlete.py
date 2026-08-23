from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import (
    set_coach_for_athlete, 
    get_user, 
    get_athlete_active_plan, 
    create_workout_plan, 
    search_exercises, 
    add_exercise_to_plan
)

athlete_router = Router()

# ==========================================
# 1. تعریف ماشین‌های حالت (FSM) برای ساخت برنامه
# ==========================================
class SoloPlanForm(StatesGroup):
    title = State()
    duration = State()

class AddExerciseForm(StatesGroup):
    plan_id = State()
    search_query = State()
    exercise_id = State()
    exercise_name = State()
    day_number = State()
    sets = State()
    reps = State()
    rest_time = State()

# ==========================================
# 2. کیبوردهای اصلی (پایین صفحه)
# ==========================================
def get_athlete_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 شروع تمرین امروز")],
            [KeyboardButton(text="📝 ساخت برنامه جدید"), KeyboardButton(text="➕ اضافه کردن حرکت به برنامه")],
            [KeyboardButton(text="👨‍🏫 اطلاعات مربی من"), KeyboardButton(text="📈 پیشرفت من")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ انصراف")]], resize_keyboard=True)

# ==========================================
# 3. دکمه‌های منوی اصلی
# ==========================================
@athlete_router.message(F.text == "🚀 شروع تمرین امروز")
async def handle_start_workout_btn(message: types.Message):
    plan = get_athlete_active_plan(message.from_user.id)
    if not plan:
        await message.answer("❌ تو هنوز هیچ برنامه فعالی نداری!\nاول از منوی پایین روی «📝 ساخت برنامه جدید» کلیک کن تا برنامه‌ت رو بچینیم.")
        return
    await message.answer("🔥 همه‌چیز آماده‌ست! برای شروع تمرینت روی این دستور کلیک کن:\n👉 /start_workout")

@athlete_router.message(F.text == "👨‍🏫 اطلاعات مربی من")
async def handle_my_coach(message: types.Message):
    user = get_user(message.from_user.id)
    if user and user.get('coach_id'):
        coach = get_user(user['coach_id'])
        if coach:
            await message.answer(f"👨‍🏫 مربی شما: **{coach['name']}**", parse_mode="Markdown")
            return
    await message.answer("❌ تو در حال حاضر به تنهایی تمرین می‌کنی و مربی نداری.\nاگر آیدی مربی رو داری، بفرست: `/setcoach 123456789`", parse_mode="Markdown")

@athlete_router.message(F.text == "📈 پیشرفت من")
async def handle_progress(message: types.Message):
    await message.answer("این بخش به زودی با نمودارهای جذاب آماده میشه! 🚧")

@athlete_router.message(F.text == "❌ انصراف")
async def cancel_any_flow(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🚫 عملیات لغو شد. به منوی اصلی برگشتیم:", reply_markup=get_athlete_main_keyboard())

# ==========================================
# 4. چرخه ساخت برنامه جدید
# ==========================================
@athlete_router.message(F.text == "📝 ساخت برنامه جدید")
async def start_create_plan(message: types.Message, state: FSMContext):
    await state.set_state(SoloPlanForm.title)
    await message.answer(
        "📝 خیلی هم عالی! بیا یک برنامه جدید بسازیم.\n\n"
        "اول از همه یک **اسم** برای برنامه‌ت بنویس (مثلاً: برنامه حجمی ماه اول):",
        reply_markup=get_cancel_keyboard()
    )

@athlete_router.message(SoloPlanForm.title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(SoloPlanForm.duration)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="30"), KeyboardButton(text="45"), KeyboardButton(text="60")], [KeyboardButton(text="❌ انصراف")]],
        resize_keyboard=True
    )
    await message.answer("⏳ این برنامه برای **چند روز** طراحی میشه؟ (یکی از دکمه‌ها رو بزن یا عدد تایپ کن)", reply_markup=kb)

@athlete_router.message(SoloPlanForm.duration)
async def process_duration(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❌ لطفاً فقط عدد وارد کن!")
        
    data = await state.get_data()
    # ساخت برنامه در دیتابیس
    plan = create_workout_plan(
        coach_id=message.from_user.id, # چون خودش مربی خودشه
        athlete_id=message.from_user.id,
        title=data['title'],
        duration_days=int(message.text)
    )
    
    await state.clear()
    
    if plan:
        await state.set_state(AddExerciseForm.search_query)
        await state.update_data(plan_id=plan['id'])
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🏁 پایان ساخت برنامه")]], resize_keyboard=True)
        await message.answer(
            f"✅ برنامه **{data['title']}** با موفقیت ساخته شد!\n\n"
            "حالا باید حرکات رو بهش اضافه کنیم.\n"
            "🔍 **اسم حرکتی که می‌خوای رو بفرست** (مثلا بنویس: پرس سینه):",
            reply_markup=kb, parse_mode="Markdown"
        )
    else:
        await message.answer("❌ خطایی رخ داد.", reply_markup=get_athlete_main_keyboard())

# ==========================================
# 5. چرخه جستجو و اضافه کردن حرکات
# ==========================================
@athlete_router.message(F.text == "➕ اضافه کردن حرکت به برنامه")
async def trigger_add_exercise(message: types.Message, state: FSMContext):
    plan = get_athlete_active_plan(message.from_user.id)
    if not plan:
        return await message.answer("❌ تو برنامه فعالی نداری! اول «📝 ساخت برنامه جدید» رو بزن.", reply_markup=get_athlete_main_keyboard())
        
    await state.set_state(AddExerciseForm.search_query)
    await state.update_data(plan_id=plan['id'])
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🏁 پایان ساخت برنامه")]], resize_keyboard=True)
    await message.answer("🔍 **اسم حرکتی که می‌خوای رو سرچ کن** (مثلا بنویس: اسکوات):", reply_markup=kb, parse_mode="Markdown")

@athlete_router.message(F.text == "🏁 پایان ساخت برنامه")
async def finish_plan_creation(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🎉 برنامه‌ت تکمیل شد! خسته نباشی قهرمان.\nاز منوی زیر می‌تونی تمرینت رو شروع کنی:", reply_markup=get_athlete_main_keyboard())

@athlete_router.message(AddExerciseForm.search_query)
async def search_exercise_for_plan(message: types.Message, state: FSMContext):
    results = search_exercises(message.text)
    if not results:
        return await message.answer("❌ حرکتی با این اسم تو دیتابیس پیدا نکردم. یه کلمه دیگه سرچ کن:")
        
    # ساخت دکمه‌های شیشه‌ای برای نتایج جستجو
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[])
    for ex in results:
        inline_kb.inline_keyboard.append([InlineKeyboardButton(text=ex['name'], callback_data=f"sel_ex:{ex['id']}")])
        
    await message.answer("👇 حرکات پیدا شده! یکی رو انتخاب کن:", reply_markup=inline_kb)

@athlete_router.callback_query(F.data.startswith("sel_ex:"))
async def select_exercise_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'plan_id' not in data:
        return await callback_query.answer("❌ اول روی دکمه اضافه کردن حرکت کلیک کن.", show_alert=True)
        
    ex_id = callback_query.data.split(":")[1]
    ex_name = next((btn.text for row in callback_query.message.reply_markup.inline_keyboard for btn in row if btn.callback_data == callback_query.data), "حرکت انتخاب شده")

    await state.update_data(exercise_id=ex_id, exercise_name=ex_name)
    await state.set_state(AddExerciseForm.day_number)
    await callback_query.answer()
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")], 
                  [KeyboardButton(text="4"), KeyboardButton(text="5"), KeyboardButton(text="6")], 
                  [KeyboardButton(text="❌ انصراف")]], resize_keyboard=True
    )
    await callback_query.message.answer(f"✅ حرکت **{ex_name}** انتخاب شد.\n\n📅 این حرکت برای **روز چندم** تمرینه؟", reply_markup=kb, parse_mode="Markdown")

@athlete_router.message(AddExerciseForm.day_number)
async def process_day_number(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("❌ فقط عدد بفرست!")
    await state.update_data(day_number=int(message.text))
    await state.set_state(AddExerciseForm.sets)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="3"), KeyboardButton(text="4"), KeyboardButton(text="5")], [KeyboardButton(text="❌ انصراف")]], resize_keyboard=True)
    await message.answer("🔢 چند **ست** می‌خوای بزنی؟", reply_markup=kb)

@athlete_router.message(AddExerciseForm.sets)
async def process_sets(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("❌ فقط عدد بفرست!")
    await state.update_data(sets=int(message.text))
    await state.set_state(AddExerciseForm.reps)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="8"), KeyboardButton(text="10"), KeyboardButton(text="12")], [KeyboardButton(text="15"), KeyboardButton(text="تا ناتوانی")], [KeyboardButton(text="❌ انصراف")]], resize_keyboard=True)
    await message.answer("🔄 چند **تکرار**؟ (می‌تونی عدد بزنی یا انتخاب کنی)", reply_markup=kb)

@athlete_router.message(AddExerciseForm.reps)
async def process_reps(message: types.Message, state: FSMContext):
    await state.update_data(reps=message.text)
    await state.set_state(AddExerciseForm.rest_time)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="30"), KeyboardButton(text="45"), KeyboardButton(text="60")], [KeyboardButton(text="90"), KeyboardButton(text="120")], [KeyboardButton(text="❌ انصراف")]], resize_keyboard=True)
    await message.answer("⏱ زمان **استراحت** بین ست‌ها (به ثانیه) چقدر باشه؟", reply_markup=kb)

@athlete_router.message(AddExerciseForm.rest_time)
async def process_rest(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("❌ فقط عدد بفرست (مثلا 60)!")
    data = await state.get_data()
    
    # ذخیره حرکت در برنامه
    add_exercise_to_plan(
        plan_id=data['plan_id'],
        day_number=data['day_number'],
        exercise_id=data['exercise_id'],
        sets=data['sets'],
        reps=data['reps'],
        rest_time=int(message.text)
    )
    
    # برگشت به حالت سرچ برای حرکت بعدی
    await state.set_state(AddExerciseForm.search_query)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🏁 پایان ساخت برنامه")]], resize_keyboard=True)
    await message.answer(
        f"✅ حرکت **{data['exercise_name']}** با موفقیت به برنامه اضافه شد!\n\n"
        "🔍 برای اضافه کردن حرکت بعدی، **اسم حرکت جدید رو سرچ کن** یا دکمه پایان رو بزن:",
        reply_markup=kb, parse_mode="Markdown"
    )
