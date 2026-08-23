from supabase import create_client, Client
from datetime import datetime, timedelta
import config

# اتصال به سوپابیس
supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def get_user(telegram_id: int):
    response = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    return response.data[0] if response.data else None

def create_user(telegram_id: int, name: str, role: str = "athlete"):
    data = {
        "telegram_id": telegram_id,
        "name": name,
        "role": role,
        "coach_id": None
    }
    response = supabase.table("users").insert(data).execute()
    return response.data

def update_user_role(telegram_id: int, new_role: str):
    response = supabase.table("users").update({"role": new_role}).eq("telegram_id", telegram_id).execute()
    return response.data

def get_all_users():
    response = supabase.table("users").select("telegram_id").execute()
    return response.data

def get_coach_athletes(coach_id: int):
    response = supabase.table("users").select("telegram_id, name").eq("coach_id", coach_id).execute()
    return response.data

def save_assessment(data: dict):
    # اول بررسی می‌کنیم که آیا کاربر قبلاً فرمی داشته یا نه
    existing = supabase.table("assessments").select("id").eq("telegram_id", data["telegram_id"]).execute()
    
    if existing.data:
        # اگه قبلاً فرم داشته، اطلاعاتش رو آپدیت می‌کنیم
        response = supabase.table("assessments").update(data).eq("telegram_id", data["telegram_id"]).execute()
    else:
        # اگه بار اولشه، یک فرم جدید می‌سازیم
        response = supabase.table("assessments").insert(data).execute()
        
    return response.data
def set_coach_for_athlete(athlete_id: int, coach_id: int):
    response = supabase.table("users").update({"coach_id": coach_id}).eq("telegram_id", athlete_id).execute()
    return response.data

def search_exercises(query: str):
    response = supabase.table("exercises").select("*").ilike("name", f"%{query}%").limit(15).execute()
    return response.data

def update_exercise_media(exercise_id: str, media_file_id: str):
    response = supabase.table("exercises").update({"media_file_id": media_file_id}).eq("id", exercise_id).execute()
    return response.data

def create_workout_plan(coach_id: int, athlete_id: int, title: str, duration_days: int):
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
    target_date = (datetime.utcnow() + timedelta(days=days_left)).strftime('%Y-%m-%d')
    response = supabase.table("workout_plans").select("*").eq("status", "active").eq("end_date", target_date).execute()
    return response.data

def get_latest_plan_by_coach(coach_id: int):
    response = supabase.table("workout_plans").select("*").eq("coach_id", coach_id).order("created_at", desc=True).limit(1).execute()
    return response.data[0] if response.data else None

def add_exercise_to_plan(plan_id: str, day_number: int, exercise_id: str, sets: int, reps: str, rest_time: int):
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

def get_athlete_active_plan(athlete_id: int):
    response = supabase.table("workout_plans").select("*").eq("athlete_id", athlete_id).eq("status", "active").execute()
    return response.data[0] if response.data else None

def get_exercises_for_plan(plan_id: str):
    response = supabase.table("plan_exercises").select("*, exercise_id(*)").eq("plan_id", plan_id).order("day_number").execute()
    return response.data

def log_exercise_set(athlete_id: int, exercise_name: str, set_number: int, reps_done: int, weight_used: float):
    data = {
        "athlete_id": athlete_id,
        "exercise_name": exercise_name,
        "set_number": set_number,
        "reps_done": reps_done,
        "weight_used": weight_used
    }
    supabase.table("set_logs").insert(data).execute()

def get_athlete_logs(athlete_id: int):
    response = supabase.table("set_logs").select("*").eq("athlete_id", athlete_id).execute()
    return response.data

def add_custom_exercise(name: str, created_by: int):
    """ثبت حرکت جدید در دیتابیس توسط کاربر"""
    data = {
        "name": name,
        "sport_type": "شخصی",
        "created_by": created_by
    }
    response = supabase.table("exercises").insert(data).execute()
    return response.data[0] if response.data else None
