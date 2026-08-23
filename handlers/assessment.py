from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from database import save_assessment

assessment_router = Router()

class AssessmentForm(StatesGroup):
    full_name = State()
    age = State()
    gender = State()
    height = State()
    weight = State()
    ask_continue = State() # استیت جدید برای پرسش ادامه دادن یا ندادن
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

def make_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=item)] for item in items]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

async def start_assessment(message: types.Message, state: FSMContext):
    await message.answer("📝 برای تنظیم پروفایل ورزشیت، به چند تا سوال پایه جواب بده.\n\n۱. نام و نام خانوادگی خودت رو وارد کن:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AssessmentForm.full_name)

@assessment_router.message(AssessmentForm.full_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(AssessmentForm.age)
    await message.answer("۲. سن شما چقدره؟ (به عدد)")

@assessment_router.message(AssessmentForm.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text) if message.text.isdigit() else 0)
    await state.set_state(AssessmentForm.gender)
    await message.answer("۳. جنسیت خودت رو انتخاب کن:", reply_markup=make_keyboard(["مرد", "زن"]))

@assessment_router.message(AssessmentForm.gender)
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await state.set_state(AssessmentForm.height)
    await message.answer("۴. قد شما چقدره؟ (به سانتی‌متر)", reply_markup=ReplyKeyboardRemove())

@assessment_router.message(AssessmentForm.height)
async def process_height(message: types.Message, state: FSMContext):
    await state.update_data(height=float(message.text) if message.text.replace('.','',1).isdigit() else 0)
    await state.set_state(AssessmentForm.weight)
    await message.answer("۵. وزن شما چقدره؟ (به کیلوگرم)")

@assessment_router.message(AssessmentForm.weight)
async def process_weight(message: types.Message, state: FSMContext):
    await state.update_data(weight=float(message.text) if message.text.replace('.','',1).isdigit() else 0)
    
    # اینجا از کاربر می‌پرسیم که آیا می‌خواد فرم رو ادامه بده یا نه
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="بله، بریم سراغ بقیه سوالات 📝")],
            [KeyboardButton(text="پایان فرم و ثبت همین اطلاعات ⏭️")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(AssessmentForm.ask_continue)
    await message.answer("✅ اطلاعات پایه‌ی شما ثبت شد!\nحدود ۱۵ سوال تخصصی دیگه (مثل سوابق ورزشی و آسیب‌دیدگی‌ها) باقی مونده. می‌خوای الان جواب بدی یا همین‌جا فرم رو ببندیم؟", reply_markup=keyboard)

@assessment_router.message(AssessmentForm.ask_continue)
async def process_ask_continue(message: types.Message, state: FSMContext):
    if "پایان" in message.text:
        # اگر اسکیپ کرد، اطلاعات رو همونطور که هست ذخیره می‌کنیم
        data = await state.get_data()
        data['telegram_id'] = message.from_user.id
        # این خط رو قبل از try: save_assessment(data) بذار
        await message.answer("⏳ در حال پردازش...", reply_markup=ReplyKeyboardRemove())
        try:
            save_assessment(data)
            # نمایش دکمه‌های شیشه‌ای برای انتخاب مسیر بعدی
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👨‍🏫 می‌خوام مربی انتخاب کنم", callback_data="choose_coach_flow")],
                [InlineKeyboardButton(text="🏋️‍♂️ خودم به تنهایی تمرین می‌کنم", callback_data="solo_training_flow")]
            ])
            await message.answer("🎉 **پروفایل ورزشی تو با موفقیت ساخته شد!** 🥳\n\nحالا به من بگو دوست داری چطوری پیش بری؟", reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            await message.answer("❌ متاسفانه در ثبت اطلاعات مشکلی پیش آمد.")
        await state.clear()
    else:
        # اگر خواست ادامه بده، می‌ریم سراغ سوالات تخصصی
        await state.set_state(AssessmentForm.occupation)
        await message.answer("۶. شغل شما چیست؟", reply_markup=ReplyKeyboardRemove())

# --- ادامه فرم تخصصی ---
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
    await message.answer("۹. آیا برای این هدف زمان خاصی در نظر دارید؟", reply_markup=ReplyKeyboardRemove())

@assessment_router.message(AssessmentForm.goal_timeframe)
async def process_timeframe(message: types.Message, state: FSMContext):
    await state.update_data(goal_timeframe=message.text)
    await state.set_state(AssessmentForm.previous_programs)
    await message.answer("۱۰. آیا قبلاً از برنامه تمرینی پیروی کرده‌اید؟")

@assessment_router.message(AssessmentForm.previous_programs)
async def process_prev_programs(message: types.Message, state: FSMContext):
    await state.update_data(previous_programs=message.text)
    await state.set_state(AssessmentForm.diseases)
    await message.answer("۱۱. آیا بیماری خاصی دارید؟ (در غیر این صورت بنویسید خیر)")

@assessment_router.message(AssessmentForm.diseases)
async def process_diseases(message: types.Message, state: FSMContext):
    await state.update_data(diseases=message.text)
    await state.set_state(AssessmentForm.medications)
    await message.answer("۱۲. آیا داروی خاصی مصرف می‌کنید؟")

@assessment_router.message(AssessmentForm.medications)
async def process_meds(message: types.Message, state: FSMContext):
    await state.update_data(medications=message.text)
    await state.set_state(AssessmentForm.injuries)
    await message.answer("۱۳. آیا محدودیت حرکتی یا آسیب‌دیدگی دارید؟")

@assessment_router.message(AssessmentForm.injuries)
async def process_injuries(message: types.Message, state: FSMContext):
    await state.update_data(injuries=message.text)
    await state.set_state(AssessmentForm.sleep_hours)
    await message.answer("۱۴. میانگین خواب شبانه شما چند ساعت است؟")

@assessment_router.message(AssessmentForm.sleep_hours)
async def process_sleep(message: types.Message, state: FSMContext):
    await state.update_data(sleep_hours=float(message.text) if message.text.replace('.','',1).isdigit() else 0)
    await state.set_state(AssessmentForm.experience_level)
    await message.answer("۱۵. سابقه ورزشی شما چقدر است؟", reply_markup=make_keyboard(["تازه‌کار", "متوسط", "حرفه‌ای"]))

@assessment_router.message(AssessmentForm.experience_level)
async def process_exp(message: types.Message, state: FSMContext):
    await state.update_data(experience_level=message.text)
    await state.set_state(AssessmentForm.main_sport)
    await message.answer("۱۶. ورزشی که بیشتر انجام می‌دهید چیست؟", reply_markup=ReplyKeyboardRemove())

@assessment_router.message(AssessmentForm.main_sport)
async def process_main_sport(message: types.Message, state: FSMContext):
    await state.update_data(main_sport=message.text)
    await state.set_state(AssessmentForm.sessions_per_week)
    await message.answer("۱۷. در حال حاضر چند جلسه در هفته ورزش می‌کنید؟")

@assessment_router.message(AssessmentForm.sessions_per_week)
async def process_sessions(message: types.Message, state: FSMContext):
    await state.update_data(sessions_per_week=int(message.text) if message.text.isdigit() else 0)
    await state.set_state(AssessmentForm.session_duration)
    await message.answer("۱۸. مدت زمان هر جلسه تمرین چقدر است؟ (به دقیقه)")

@assessment_router.message(AssessmentForm.session_duration)
async def process_duration(message: types.Message, state: FSMContext):
    await state.update_data(session_duration=int(message.text) if message.text.isdigit() else 0)
    await state.set_state(AssessmentForm.previous_coach)
    await message.answer("۱۹. آیا سابقه تمرین زیر نظر مربی دارید؟")

@assessment_router.message(AssessmentForm.previous_coach)
async def process_prev_coach(message: types.Message, state: FSMContext):
    await state.update_data(previous_coach=message.text)
    await state.set_state(AssessmentForm.preferred_days)
    await message.answer("۲۰. ترجیح می‌دهید چند روز در هفته تمرین کنید؟")

@assessment_router.message(AssessmentForm.preferred_days)
async def process_pref_days(message: types.Message, state: FSMContext):
    await state.update_data(preferred_days=int(message.text) if message.text.isdigit() else 0)
    await state.set_state(AssessmentForm.equipment)
    await message.answer("۲۱. چه تجهیزاتی در اختیار دارید؟", reply_markup=make_keyboard(["باشگاه کامل", "تجهیزات خانگی", "وزن بدن"]))

@assessment_router.message(AssessmentForm.equipment)
async def process_equip(message: types.Message, state: FSMContext):
    await state.update_data(equipment=message.text)
    await state.set_state(AssessmentForm.wants_cardio)
    await message.answer("۲۲. آیا تمرینات هوازی (Cardio) هم می‌خواید؟", reply_markup=make_keyboard(["بله", "خیر"]))

@assessment_router.message(AssessmentForm.wants_cardio)
async def process_wants_cardio(message: types.Message, state: FSMContext):
    await state.update_data(wants_cardio=message.text)
    
    # اگه کاربر هوازی نخواست، سوال بعدی رو اسکیپ می‌کنیم
    if message.text == "خیر":
        await state.update_data(preferred_cardio="ندارد")
        await state.set_state(AssessmentForm.daily_time)
        await message.answer("۲۴. ⏱ روزانه چقدر زمان می‌تونی برای تمرین بگذاری؟ (به دقیقه)", reply_markup=ReplyKeyboardRemove())
    else:
        await state.set_state(AssessmentForm.preferred_cardio)
        await message.answer("۲۳. 🏃‍♂️ با کدوم هوازی راحت‌تری؟", reply_markup=make_keyboard(["تردمیل", "دوچرخه", "الپتیکال", "طناب", "فرقی ندارد"]))

@assessment_router.message(AssessmentForm.preferred_cardio)
async def process_pref_cardio(message: types.Message, state: FSMContext):
    await state.update_data(preferred_cardio=message.text)
    await state.set_state(AssessmentForm.daily_time)
    await message.answer("۲۴. روزانه چقدر زمان می‌توانید برای تمرین بگذارید؟ (به دقیقه)", reply_markup=ReplyKeyboardRemove())

@assessment_router.message(AssessmentForm.daily_time)
async def process_daily_time(message: types.Message, state: FSMContext):
    await state.update_data(daily_time=int(message.text) if message.text.isdigit() else 0)
    
    data = await state.get_data()
    data['telegram_id'] = message.from_user.id
    
    try:
        save_assessment(data)
        # همون دکمه‌های شیشه‌ای پایان فرم
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👨‍🏫 می‌خوام مربی انتخاب کنم", callback_data="choose_coach_flow")],
            [InlineKeyboardButton(text="🏋️‍♂️ خودم به تنهایی تمرین می‌کنم", callback_data="solo_training_flow")]
        ])
        await message.answer("🎉 **پروفایل ورزشی تو با موفقیت ساخته شد!** 🥳\n\nحالا به من بگو دوست داری چطوری پیش بری؟", reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        await message.answer("❌ متاسفانه در ثبت اطلاعات مشکلی پیش آمد.")
    
    await state.clear()
