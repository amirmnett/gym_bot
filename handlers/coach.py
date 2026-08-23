from aiogram import F, Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_coach_athletes, get_assessment, create_workout_plan, search_exercises, add_exercise_to_plan, add_custom_exercise

coach_router = Router()

# ==========================================
# ماشین حالت (FSM) برای نوشتن برنامه شاگرد
# ==========================================
class CoachPlanForm(StatesGroup):
    athlete_id = State()
    plan_category = State()
    plan_style = State()
    days_per_week = State()
    title = State()

class CoachAddExForm(StatesGroup):
    plan_id = State()
    search_query = State()
    exercise_id = State()
    exercise_name = State()
    day_number = State()
    sets = State()
    reps = State()
    rest_time = State()

# ==========================================
# کیبورد اصلی مربی (پایین صفحه)
# ==========================================
def get_coach_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 شاگردان من"), KeyboardButton(text="📋 فرم‌های ارزیابی")],
            [KeyboardButton(text="📝 نوشتن برنامه جدید"), KeyboardButton(text="➕ افزودن حرکت به برنامه")],
            [KeyboardButton(text="📊 نمودار پیشرفت شاگردان")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )

def get_coach_cancel_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ انصراف (مربی)")]], resize_keyboard=True)

@coach_router.message(F.text == "❌ انصراف (مربی)")
async def cancel_coach_flow(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🚫 عملیات لغو شد. به منوی مدیریت برگشتیم:", reply_markup=get_coach_main_keyboard())

# ==========================================
# دکمه‌های اصلی پنل
# ==========================================
@coach_router.message(F.text == "👥 شاگردان من")
async def show_my_athletes(message: types.Message):
    athletes = get_coach_athletes(message.from_user.id)
    if not athletes:
        return await message.answer("❌ شما در حال حاضر شاگردی ندارید.")
        
    text = "👥 **لیست شاگردان شما:**\n\n"
    for idx, ath in enumerate(athletes, 1):
        text += f"{idx}. {ath['name']} (ID: `{ath['telegram_id']}`)\n"
    await message.answer(text, parse_mode="Markdown")

@coach_router.message(F.text == "📋 فرم‌های ارزیابی")
async def show_assessment_forms(message: types.Message):
    athletes = get_coach_athletes(message.from_user.id)
    if not athletes:
        return await message.answer("❌ شاگردی برای نمایش فرم وجود ندارد.")
        
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[])
    for ath in athletes:
        inline_kb.inline_keyboard.append([InlineKeyboardButton(text=f"📋 فرم {ath['name']}", callback_data=f"view_form:{ath['telegram_id']}")])
        
    await message.answer("👇 برای مشاهده فرم ارزیابی، روی اسم شاگرد کلیک کنید:", reply_markup=inline_kb)

@coach_router.callback_query(F.data.startswith("view_form:"))
async def view_athlete_form(callback_query: types.CallbackQuery):
    athlete_id = int(callback_query.data.split(":")[1])
    form = get_assessment(athlete_id)
    
    if not form:
        return await callback_query.answer("❌ این شاگرد هنوز فرمی پر نکرده است.", show_alert=True)
        
    text = (
        f"📋 **فرم ارزیابی:**\n\n"
        f"👤 **نام:** {form.get('full_name', 'نامشخص')}\n"
        f"📅 **سن:** {form.get('age', '-')} | 📏 **قد:** {form.get('height', '-')} | ⚖️ **وزن:** {form.get('weight', '-')}\n"
        f"🎯 **هدف:** {form.get('main_goal', '-')}\n"
        f"⚕️ **بیماری/آسیب:** {form.get('diseases', '-')} / {form.get('injuries', '-')}\n"
        f"🏃‍♂️ **روزهای تمرین:** {form.get('preferred_days', '-')} روز در هفته\n"
        f"🏋️‍♂️ **تجهیزات:** {form.get('equipment', '-')}\n"
    )
    await callback_query.message.answer(text, parse_mode="Markdown")
    await callback_query.answer()

# ==========================================
# پروسه نوشتن برنامه برای شاگرد
# ==========================================
@coach_router.message(F.text == "📝 نوشتن برنامه جدید")
async def start_writing_plan(message: types.Message, state: FSMContext):
    athletes = get_coach_athletes(message.from_user.id)
    if not athletes:
        return await message.answer("❌ اول باید شاگرد داشته باشید تا براش برنامه بنویسید.")
        
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[])
    for ath in athletes:
        inline_kb.inline_keyboard.append([InlineKeyboardButton(text=f"✍️ برنامه برای {ath['name']}", callback_data=f"write_plan:{ath['telegram_id']}")])
        
    await message.answer("👇 می‌خواید برای کدوم شاگرد برنامه بنویسید؟", reply_markup=inline_kb)

@coach_router.callback_query(F.data.startswith("write_plan:"))
async def plan_select_category(callback_query: types.CallbackQuery, state: FSMContext):
    athlete_id = int(callback_query.data.split(":")[1])
    await state.update_data(athlete_id=athlete_id)
    await state.set_state(CoachPlanForm.plan_category)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="بدنسازی"), KeyboardButton(text="کلیستنیکس")], 
                  [KeyboardButton(text="❌ انصراف (مربی)")]], resize_keyboard=True
    )
    await callback_query.message.answer("📝 **نوع برنامه** شاگرد رو انتخاب کنید:", reply_markup=kb, parse_mode="Markdown")
    await callback_query.answer()

@coach_router.message(CoachPlanForm.plan_category)
async def plan_select_style(message: types.Message, state: FSMContext):
    await state.update_data(plan_category=message.text)
    await state.set_state(CoachPlanForm.plan_style)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="فول بادی (Full Body)"), KeyboardButton(text="پوش/پول/لگ (PPL)")], 
                  [KeyboardButton(text="بالاتنه / پایین‌تنه"), KeyboardButton(text="❌ انصراف (مربی)")]], resize_keyboard=True
    )
    await message.answer("سبک تمرین رو مشخص کنید:", reply_markup=kb)

@coach_router.message(CoachPlanForm.plan_style)
async def plan_select_days(message: types.Message, state: FSMContext):
    await state.update_data(plan_style=message.text)
    await state.set_state(CoachPlanForm.days_per_week)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="3"), KeyboardButton(text="4"), KeyboardButton(text="5"), KeyboardButton(text="6")], [KeyboardButton(text="❌ انصراف (مربی)")]], resize_keyboard=True)
    await message.answer("چند روز در هفته؟", reply_markup=kb)

@coach_router.message(CoachPlanForm.days_per_week)
async def plan_select_title(message: types.Message, state: FSMContext):
    await state.update_data(days_per_week=message.text)
    await state.set_state(CoachPlanForm.title)
    await message.answer("یک **عنوان** برای برنامه بنویسید (مثلا: فاز اول چربی‌سوزی):", reply_markup=get_coach_cancel_kb())

@coach_router.message(CoachPlanForm.title)
async def plan_finish_setup(message: types.Message, state: FSMContext):
    data = await state.get_data()
    full_title = f"{message.text} ({data['plan_category']} - {data['plan_style']})"
    
    plan = create_workout_plan(
        coach_id=message.from_user.id,
        athlete_id=data['athlete_id'],
        title=full_title,
        duration_days=30
    )
    
    await state.clear()
    if plan:
        await state.set_state(CoachAddExForm.search_query)
        await state.update_data(plan_id=plan['id'])
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🏁 پایان ساخت برنامه")]], resize_keyboard=True)
        await message.answer(
            f"✅ استخوان‌بندی برنامه شاگرد ساخته شد!\n\n"
            "🔍 **اسم اولین حرکتی که می‌خواید براش بذارید رو سرچ کنید**:",
            reply_markup=kb, parse_mode="Markdown"
        )
        # اطلاع‌رسانی به شاگرد
        await message.bot.send_message(chat_id=data['athlete_id'], text=f"🎉 مربی شما یک برنامه جدید به اسم **{full_title}** براتون ایجاد کرد!")
    else:
        await message.answer("❌ خطا در ساخت برنامه.", reply_markup=get_coach_main_keyboard())

# ==========================================
# چرخه اضافه کردن حرکات (دقیقاً مشابه پنل ورزشکار)
# ==========================================
@coach_router.message(F.text == "🏁 پایان ساخت برنامه")
async def finish_coach_plan(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🎉 برنامه با موفقیت تکمیل شد!\nبه منوی مدیریت برگشتیم.", reply_markup=get_coach_main_keyboard())

@coach_router.message(CoachAddExForm.search_query)
async def search_ex_coach(message: types.Message, state: FSMContext):
    query = message.text
    results = search_exercises(query)
    
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[])
    if results:
        for ex in results:
            inline_kb.inline_keyboard.append([InlineKeyboardButton(text=ex['name'], callback_data=f"c_sel_ex:{ex['id']}")])
        inline_kb.inline_keyboard.append([InlineKeyboardButton(text=f"➕ ساخت حرکت جدید: {query}", callback_data=f"c_new_ex:{query}")])
        await message.answer("👇 انتخاب کنید:", reply_markup=inline_kb)
    else:
        inline_kb.inline_keyboard.append([InlineKeyboardButton(text=f"➕ افزودن '{query}' به دیتابیس", callback_data=f"c_new_ex:{query}")])
        await message.answer("❌ حرکتی پیدا نشد. می‌توانید آن را بسازید:", reply_markup=inline_kb)

@coach_router.callback_query(F.data.startswith("c_new_ex:"))
async def make_new_ex_coach(callback_query: types.CallbackQuery, state: FSMContext):
    ex_name = callback_query.data.split(":")[1]
    new_ex = add_custom_exercise(ex_name, callback_query.from_user.id)
    if not new_ex:
        return await callback_query.answer("❌ خطا", show_alert=True)
        
    await state.update_data(exercise_id=new_ex['id'], exercise_name=new_ex['name'])
    await state.set_state(CoachAddExForm.day_number)
    await callback_query.answer()
    
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")], [KeyboardButton(text="❌ انصراف (مربی)")]], resize_keyboard=True)
    await callback_query.message.answer(f"📅 حرکت **{new_ex['name']}** برای **روز چندم**؟", reply_markup=kb, parse_mode="Markdown")

@coach_router.callback_query(F.data.startswith("c_sel_ex:"))
async def select_ex_coach(callback_query: types.CallbackQuery, state: FSMContext):
    ex_id = callback_query.data.split(":")[1]
    ex_name = next((btn.text for row in callback_query.message.reply_markup.inline_keyboard for btn in row if btn.callback_data == callback_query.data), "حرکت")
    
    await state.update_data(exercise_id=ex_id, exercise_name=ex_name)
    await state.set_state(CoachAddExForm.day_number)
    await callback_query.answer()
    
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")], [KeyboardButton(text="❌ انصراف (مربی)")]], resize_keyboard=True)
    await callback_query.message.answer(f"📅 حرکت **{ex_name}** برای **روز چندم**؟", reply_markup=kb, parse_mode="Markdown")

@coach_router.message(CoachAddExForm.day_number)
async def c_day_num(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("❌ عدد!")
    await state.update_data(day_number=int(message.text))
    await state.set_state(CoachAddExForm.sets)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="3"), KeyboardButton(text="4"), KeyboardButton(text="5")], [KeyboardButton(text="❌ انصراف (مربی)")]], resize_keyboard=True)
    await message.answer("🔢 چند **ست**؟", reply_markup=kb)

@coach_router.message(CoachAddExForm.sets)
async def c_sets(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("❌ عدد!")
    await state.update_data(sets=int(message.text))
    await state.set_state(CoachAddExForm.reps)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="10"), KeyboardButton(text="12"), KeyboardButton(text="15"), KeyboardButton(text="تا ناتوانی")], [KeyboardButton(text="❌ انصراف (مربی)")]], resize_keyboard=True)
    await message.answer("🔄 چند **تکرار**؟", reply_markup=kb)

@coach_router.message(CoachAddExForm.reps)
async def c_reps(message: types.Message, state: FSMContext):
    await state.update_data(reps=message.text)
    await state.set_state(CoachAddExForm.rest_time)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="45"), KeyboardButton(text="60"), KeyboardButton(text="90")], [KeyboardButton(text="❌ انصراف (مربی)")]], resize_keyboard=True)
    await message.answer("⏱ زمان **استراحت** (ثانیه)؟", reply_markup=kb)

@coach_router.message(CoachAddExForm.rest_time)
async def c_rest(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("❌ عدد!")
    data = await state.get_data()
    
    add_exercise_to_plan(
        plan_id=data['plan_id'], day_number=data['day_number'], exercise_id=data['exercise_id'],
        sets=data['sets'], reps=data['reps'], rest_time=int(message.text)
    )
    
    await state.set_state(CoachAddExForm.search_query)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🏁 پایان ساخت برنامه")]], resize_keyboard=True)
    await message.answer(f"✅ اضافه شد!\n🔍 **سرچ حرکت بعدی:**", reply_markup=kb)
