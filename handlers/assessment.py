from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database import save_assessment

assessment_router = Router()

# تعریف مراحل فرم ارزیابی
class AssessmentForm(StatesGroup):
    full_name = State()
    age = State()
    gender = State()
    height = State()
    weight = State()
    occupation = State()
    activity_level = State()
    main_goal = State()
    goal_timeframe = State()
    previous_programs = State()
    diseases = State()
    medications = State()
    injuries = State()
    sleep_hours = State()
    experience_level = State()
    main_sport = State()
    sessions_per_week = State()
    session_duration = State()
    previous_coach = State()
    preferred_days = State()
    equipment = State()
    wants_cardio = State()
    preferred_cardio = State()
    daily_time = State()

# تابع کمکی برای ساخت سریع دکمه‌ها
def make_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=item)] for item in items]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


async def start_assessment(message: types.Message, state: FSMContext):
    """شروع فرم ارزیابی (این تابع را در فایل auth.py صدا می‌زنیم)"""
    await message.answer("📝 برای دریافت بهترین برنامه، لطفاً به این سوالات با دقت پاسخ بده.\n\n۱. نام و نام خانوادگی خود را وارد کن:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AssessmentForm.full_name)


@assessment_router.message(AssessmentForm.full_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(AssessmentForm.age)
    await message.answer("۲. سن شما چقدر است؟ (به عدد)")

@assessment_router.message(AssessmentForm.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text) if message.text.isdigit() else 0)
    await state.set_state(AssessmentForm.gender)
    await message.answer("۳. جنسیت خود را انتخاب کنید:", reply_markup=make_keyboard(["مرد", "زن"]))

@assessment_router.message(AssessmentForm.gender)
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await state.set_state(AssessmentForm.height)
    await message.answer("۴. قد شما چقدر است؟ (به سانتی‌متر)", reply_markup=ReplyKeyboardRemove())

@assessment_router.message(AssessmentForm.height)
async def process_height(message: types.Message, state: FSMContext):
    await state.update_data(height=float(message.text) if message.text.replace('.','',1).isdigit() else 0)
    await state.set_state(AssessmentForm.weight)
    await message.answer("۵. وزن شما چقدر است؟ (به کیلوگرم)")

@assessment_router.message(AssessmentForm.weight)
async def process_weight(message: types.Message, state: FSMContext):
    await state.update_data(weight=float(message.text) if message.text.replace('.','',1).isdigit() else 0)
    await state.set_state(AssessmentForm.occupation)
    await message.answer("۶. شغل شما چیست؟")

@assessment_router.message(AssessmentForm.occupation)
async def process_occupation(message: types.Message, state: FSMContext):
    await state.update_data(occupation=message.text)
    await state.set_state(AssessmentForm.activity_level)
    await message.answer("۷. سطح فعالیت روزانه شما چقدر است؟", reply_markup=make_keyboard(["کم", "متوسط", "زیاد"]))

@assessment_router.message(AssessmentForm.activity_level)
async def process_activity(message: types.Message, state: FSMContext):
    await state.update_data(activity_level=message.text)
    await state.set_state(AssessmentForm.main_goal)
    await message.answer("۸. هدف اصلی شما از تمرین چیست؟", reply_markup=make_keyboard(["کاهش وزن", "افزایش عضله", "افزایش قدرت", "آمادگی جسمانی", "سایر"]))

@assessment_router.message(AssessmentForm.main_goal)
async def process_main_goal(message: types.Message, state: FSMContext):
    await state.update_data(main_goal=message.text)
    await state.set_state(AssessmentForm.goal_timeframe)
    await message.answer("۹. آیا برای این هدف زمان خاصی در نظر دارید؟ (توضیح دهید یا بنویسید خیر)", reply_markup=ReplyKeyboardRemove())

@assessment_router.message(AssessmentForm.goal_timeframe)
async def process_timeframe(message: types.Message, state: FSMContext):
    await state.update_data(goal_timeframe=message.text)
    await state.set_state(AssessmentForm.previous_programs)
    await message.answer("۱۰. آیا قبلاً از برنامه تمرینی پیروی کرده‌اید؟ (اگر بله، چه برنامه‌ای؟)")

@assessment_router.message(AssessmentForm.previous_programs)
async def process_prev_programs(message: types.Message, state: FSMContext):
    await state.update_data(previous_programs=message.text)
    await state.set_state(AssessmentForm.diseases)
    await message.answer("۱۱. آیا بیماری خاصی دارید؟ (فشار خون، دیابت و... در غیر این صورت بنویسید خیر)")

@assessment_router.message(AssessmentForm.diseases)
async def process_diseases(message: types.Message, state: FSMContext):
    await state.update_data(diseases=message.text)
    await state.set_state(AssessmentForm.medications)
    await message.answer("۱۲. آیا داروی خاصی مصرف می‌کنید؟ (نام دارو، یا خیر)")

@assessment_router.message(AssessmentForm.medications)
async def process_meds(message: types.Message, state: FSMContext):
    await state.update_data(medications=message.text)
    await state.set_state(AssessmentForm.injuries)
    await message.answer("۱۳. آیا محدودیت حرکتی یا آسیب‌دیدگی دارید؟ (توضیح دهید، یا خیر)")

@assessment_router.message(AssessmentForm.injuries)
async def process_injuries(message: types.Message, state: FSMContext):
    await state.update_data(injuries=message.text)
    await state.set_state(AssessmentForm.sleep_hours)
    await message.answer("۱۴. میانگین خواب شبانه شما چند ساعت است؟ (به عدد)")

@assessment_router.message(AssessmentForm.sleep_hours)
async def process_sleep(message: types.Message, state: FSMContext):
    await state.update_data(sleep_hours=float(message.text) if message.text.replace('.','',1).isdigit() else 0)
    await state.set_state(AssessmentForm.experience_level)
    await message.answer("۱۵. سابقه ورزشی شما چقدر است؟", reply_markup=make_keyboard(["تازه‌کار", "متوسط", "حرفه‌ای"]))

@assessment_router.message(AssessmentForm.experience_level)
async def process_exp(message: types.Message, state: FSMContext):
    await state.update_data(experience_level=message.text)
    await state.set_state(AssessmentForm.main_sport)
    await message.answer("۱۶. ورزشی که بیشتر انجام می‌دهید چیست؟ (یا بنویسید هیچ)", reply_markup=ReplyKeyboardRemove())

@assessment_router.message(AssessmentForm.main_sport)
async def process_main_sport(message: types.Message, state: FSMContext):
    await state.update_data(main_sport=message.text)
    await state.set_state(AssessmentForm.sessions_per_week)
    await message.answer("۱۷. در حال حاضر چند جلسه در هفته ورزش می‌کنید؟ (به عدد)")

@assessment_router.message(AssessmentForm.sessions_per_week)
async def process_sessions(message: types.Message, state: FSMContext):
    await state.update_data(sessions_per_week=int(message.text) if message.text.isdigit() else 0)
    await state.set_state(AssessmentForm.session_duration)
    await message.answer("۱۸. مدت زمان هر جلسه تمرین چقدر است؟ (به دقیقه)")

@assessment_router.message(AssessmentForm.session_duration)
async def process_duration(message: types.Message, state: FSMContext):
    await state.update_data(session_duration=int(message.text) if message.text.isdigit() else 0)
    await state.set_state(AssessmentForm.previous_coach)
    await message.answer("۱۹. آیا سابقه تمرین زیر نظر مربی دارید؟ (اگر بله، چه مدت؟)")

@assessment_router.message(AssessmentForm.previous_coach)
async def process_prev_coach(message: types.Message, state: FSMContext):
    await state.update_data(previous_coach=message.text)
    await state.set_state(AssessmentForm.preferred_days)
    await message.answer("۲۰. ترجیح می‌دهید چند روز در هفته تمرین کنید؟ (به عدد)")

@assessment_router.message(AssessmentForm.preferred_days)
async def process_pref_days(message: types.Message, state: FSMContext):
    await state.update_data(preferred_days=int(message.text) if message.text.isdigit() else 0)
    await state.set_state(AssessmentForm.equipment)
    await message.answer("۲۱. چه تجهیزاتی در اختیار دارید؟", reply_markup=make_keyboard(["باشگاه کامل", "تجهیزات خانگی", "وزن بدن (بدون تجهیزات)"]))

@assessment_router.message(AssessmentForm.equipment)
async def process_equip(message: types.Message, state: FSMContext):
    await state.update_data(equipment=message.text)
    await state.set_state(AssessmentForm.wants_cardio)
    await message.answer("۲۲. آیا می‌خواهید تمرینات هوازی (Cardio) هم داشته باشید؟", reply_markup=make_keyboard(["بله", "خیر"]))

@assessment_router.message(AssessmentForm.wants_cardio)
async def process_wants_cardio(message: types.Message, state: FSMContext):
    await state.update_data(wants_cardio=message.text)
    await state.set_state(AssessmentForm.preferred_cardio)
    await message.answer("۲۳. با کدام هوازی راحت‌ترید؟", reply_markup=make_keyboard(["تردمیل", "دوچرخه", "الپتیکال", "طناب", "فرقی ندارد"]))

@assessment_router.message(AssessmentForm.preferred_cardio)
async def process_pref_cardio(message: types.Message, state: FSMContext):
    await state.update_data(preferred_cardio=message.text)
    await state.set_state(AssessmentForm.daily_time)
    await message.answer("۲۴. روزانه چقدر زمان می‌توانید برای تمرین بگذارید؟ (به دقیقه)", reply_markup=ReplyKeyboardRemove())

@assessment_router.message(AssessmentForm.daily_time)
async def process_daily_time(message: types.Message, state: FSMContext):
    await state.update_data(daily_time=int(message.text) if message.text.isdigit() else 0)
    
    # دریافت کل داده‌ها و ذخیره در دیتابیس
    data = await state.get_data()
    data['telegram_id'] = message.from_user.id
    
    try:
        save_assessment(data)
        await message.answer("✅ ارزیابی شما با موفقیت ثبت شد! اطلاعات شما برای مربی ارسال خواهد شد.")
    except Exception as e:
        await message.answer("❌ متاسفانه در ثبت اطلاعات مشکلی پیش آمد. لطفا به ادمین اطلاع دهید.")
        print(f"Error saving assessment: {e}")
    
    # پایان State
    await state.clear()س
