from supabase import create_client, Client
import config

# اتصال به سوپابیس
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def get_user(telegram_id: int):
    """دریافت اطلاعات کاربر از دیتابیس"""
    response = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    return response.data[0] if response.data else None

def create_user(telegram_id: int, name: str, role: str = "athlete"):
    """ثبت کاربر جدید"""
    data = {
        "telegram_id": telegram_id,
        "name": name,
        "role": role, # athlete, coach, admin
        "coach_id": None
    }
    response = supabase.table("users").insert(data).execute()
    return response.data

def save_assessment(data: dict):
    """ذخیره فرم ارزیابی ورزشکار در دیتابیس"""
    response = supabase.table("assessments").insert(data).execute()
    return response.data

def update_user_role(telegram_id: int, new_role: str):
    """تغییر نقش کاربر (مثلا ارتقا به مربی)"""
    response = supabase.table("users").update({"role": new_role}).eq("telegram_id", telegram_id).execute()
    return response.data

def get_all_users():
    """دریافت لیست تمام کاربران برای پیام سراسری"""
    response = supabase.table("users").select("telegram_id").execute()
    return response.data

def get_coach_athletes(coach_id: int):
    """دریافت لیست شاگردان یک مربی"""
    response = supabase.table("users").select("telegram_id, name").eq("coach_id", coach_id).execute()
    return response.data
def set_coach_for_athlete(athlete_id: int, coach_id: int):
    """ثبت مربی برای ورزشکار"""
    response = supabase.table("users").update({"coach_id": coach_id}).eq("telegram_id", athlete_id).execute()
    return response.data

def search_exercises(query: str):


from datetime import datetime, timedelta

def create_workout_plan(coach_id: int, athlete_id: int, title: str, duration_days: int):
    """ایجاد یک برنامه جدید در دیتابیس"""
    data = {
        "coach_id": coach_id,
        "athlete_id": athlete_id,
        "title": title,
        "duration_days": duration_days,
        "status": "active"
    }
    response = supabase.table("workout_plans").insert(data).execute()
    return response.data[0] if response.data else None

def get_expiring_plans(days_left: int):
    """پیدا کردن برنامه‌هایی که دقیقاً x روز به پایانشان مانده"""
    target_date = (datetime.utcnow() + timedelta(days=days_left)).strftime('%Y-%m-%d')
    # جستجو در دیتابیس برای برنامه‌های فعال که تاریخ پایان آن‌ها برابر با هدف است
    response = supabase.table("workout_plans").select("*").eq("status", "active").eq("end_date", target_date).execute()
    return response.data    
    
    """جستجوی حرکات ورزشی (برای پاپ‌آپ)"""
    # جستجو بر اساس نام حرکت که شامل حروف تایپ شده باشد
    response = supabase.table("exercises").select("*").ilike("name", f"%{query}%").limit(15).execute()
    return response.data

    def get_latest_plan_by_coach(coach_id: int):
    """دریافت آخرین برنامه‌ای که مربی در حال ساخت آن است"""
    response = supabase.table("workout_plans").select("*").eq("coach_id", coach_id).order("created_at", desc=True).limit(1).execute()
    return response.data[0] if response.data else None

def add_exercise_to_plan(plan_id: str, day_number: int, exercise_id: str, sets: int, reps: str, rest_time: int):
    """اضافه کردن یک حرکت با جزئیات به برنامه ورزشکار"""
    data = {
        "plan_id": plan_id,
        "day_number": day_number,
        "exercise_id": exercise_id,
        "sets": sets,
        "reps": reps,
        "rest_time": rest_time
    }
    response = supabase.table("plan_exercises").insert(data).execute()
    return response.data
