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
