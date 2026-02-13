"""
سكربت اختبار - إرسال دعوة ملتقى الكفاءات التقنية
"""
import os
import sys
import json

# تحميل المتغيرات
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from webhook_server import send_single_invitation, format_saudi_phone, JOB_FAIR_CONTENT_SID

# الرقم المستهدف
PHONE = "0554299950"
NAME = "مستخدم اختبار"

def main():
    print("=" * 50)
    print("🧪 اختبار إرسال دعوة ملتقى الكفاءات التقنية")
    print("=" * 50)
    
    formatted = format_saudi_phone(PHONE)
    if not formatted:
        print("❌ رقم الهاتف غير صحيح:", PHONE)
        return 1
    
    print(f"📱 الرقم: {PHONE} → {formatted}")
    print(f"👤 الاسم: {NAME}")
    print(f"📋 Content SID: {JOB_FAIR_CONTENT_SID}")
    print()
    print("⏳ جاري الإرسال...")
    
    success, result, msg_type = send_single_invitation(formatted, NAME)
    
    if success:
        print("=" * 50)
        print("✅ تم الإرسال بنجاح!")
        print(f"   Message SID: {result}")
        print(f"   النوع: {msg_type}")
        print("=" * 50)
        print("📲 تحقق من واتساب الرقم:", PHONE)
        return 0
    else:
        print("=" * 50)
        print("❌ فشل الإرسال!")
        print(f"   الخطأ: {result}")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(main())
