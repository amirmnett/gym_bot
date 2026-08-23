from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
import hashlib
from database import search_exercises

inline_router = Router()

@inline_router.inline_query()
async def search_exercise_inline(inline_query: InlineQuery):
    query_text = inline_query.query.strip()
    
    # اگر چیزی تایپ نکرده بود، فعلا هیچی نشون نده یا میتونی چندتا حرکت پیش‌فرض بیاری
    if not query_text:
        return

    # دریافت حرکات از دیتابیس
    results = search_exercises(query_text)
    
    inline_results = []
    for ex in results:
        # ساخت یک آیدی یونیک برای هر نتیجه
        result_id = hashlib.md5(ex['id'].encode()).hexdigest()
        
        # متنی که با کلیک روی حرکت ارسال میشه (آیدی حرکت رو میفرسته تا بات بفهمه چی انتخاب شده)
        input_content = InputTextMessageContent(
            message_text=f"/add_exercise {ex['id']}\n✅ حرکت {ex['name']} انتخاب شد."
        )
        
        # ساخت آیتم پاپ‌آپ
        article = InlineQueryResultArticle(
            id=result_id,
            title=ex['name'],
            description=f"عضله هدف: {ex['target_muscle']} | نوع: {ex['sport_type']}",
            input_message_content=input_content
        )
        inline_results.append(article)

    # نمایش نتایج به کاربر (حداکثر ۵۰ نتیجه در هر صفحه)
    await inline_query.answer(inline_results, cache_time=5, is_personal=True)
