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
