import matplotlib.pyplot as plt
import io

def generate_progress_chart(dates: list, volumes: list, title: str):
    """
    دریافت تاریخ‌ها و حجم تمرین (وزنه × تکرار) و خروجی عکس نمودار
    """
    plt.figure(figsize=(8, 5))
    plt.plot(dates, volumes, marker='o', color='b', linestyle='-', linewidth=2)
    
    plt.title(title, fontsize=14, fontname='Arial')
    plt.xlabel('Dates', fontsize=12)
    plt.ylabel('Training Volume (kg)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right') # <--- این خط دقیقاً اینجا قرار می‌گیره
    
    # ذخیره نمودار در حافظه (بدون نیاز به ذخیره فایل روی سرور)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf
