"""
فحص تفاصيل رسالة معينة
"""
import os
import sys
from dotenv import load_dotenv
from twilio.rest import Client

# إصلاح ترميز الطرفية في Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

# إعدادات Twilio
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

# الرسالة الأخيرة الفاشلة
MESSAGE_SID = "MMee31fa632b8d1aafcc9baf5f418091ea"

print("=" * 80)
print("🔍 فحص تفاصيل الرسالة الفاشلة")
print("=" * 80)
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    print(f"⏳ جاري جلب تفاصيل الرسالة: {MESSAGE_SID}")
    print()
    
    # جلب الرسالة
    message = client.messages(MESSAGE_SID).fetch()
    
    print("=" * 80)
    print("📨 تفاصيل الرسالة الكاملة:")
    print("=" * 80)
    print()
    print(f"Message SID:      {message.sid}")
    print(f"من:              {message.from_}")
    print(f"إلى:             {message.to}")
    print(f"الحالة:          {message.status}")
    print(f"كود الخطأ:       {message.error_code}")
    print(f"رسالة الخطأ:     {message.error_message}")
    print(f"وقت الإرسال:     {message.date_sent}")
    print(f"وقت الإنشاء:     {message.date_created}")
    print(f"وقت التحديث:     {message.date_updated}")
    print(f"السعر:           {message.price} {message.price_unit}")
    print(f"عدد الأجزاء:     {message.num_segments}")
    print(f"عدد الوسائط:     {message.num_media}")
    print()
    
    # محاولة الحصول على معلومات القالب
    print("=" * 80)
    print("📋 معلومات القالب:")
    print("=" * 80)
    print()
    
    # الرسالة قد تحتوي على معلومات القالب
    if hasattr(message, 'content_sid'):
        print(f"Content SID: {message.content_sid}")
    else:
        print("Content SID: غير متوفر في الكائن")
    
    # جلب تفاصيل إضافية
    print()
    print("=" * 80)
    print("🔍 محاولة جلب معلومات إضافية:")
    print("=" * 80)
    print()
    
    # عرض جميع الخصائص المتاحة
    print("الخصائص المتاحة:")
    for attr in dir(message):
        if not attr.startswith('_') and not callable(getattr(message, attr)):
            try:
                value = getattr(message, attr)
                if value and str(value) != 'None':
                    print(f"  {attr}: {value}")
            except:
                pass
    
    print()
    print("=" * 80)
    print("💡 تفسير الخطأ 63019:")
    print("=" * 80)
    print()
    print("كود الخطأ 63019 يعني: 'Template message rejected by WhatsApp'")
    print()
    print("الأسباب المحتملة:")
    print("  1. القالب غير معتمد بشكل كامل من WhatsApp")
    print("  2. Content SID المستخدم غير صحيح أو منتهي")
    print("  3. المتغيرات المرسلة لا تطابق القالب المعتمد")
    print("  4. القالب يحتوي على محتوى محظور (مثل صورة مخالفة)")
    print("  5. مشكلة في نوع القالب (Card قد لا يكون مدعوماً)")
    print()
    
    print("=" * 80)
    print("✅ الحل المقترح:")
    print("=" * 80)
    print()
    print("1. استخدم القالب الأساسي المجرّب:")
    print("   python test_working_template.py")
    print()
    print("2. تحقق من اعتماد القالب في WhatsApp Business Manager:")
    print("   https://business.facebook.com")
    print()
    print("3. إذا كنت تستخدم قالب VIP Card:")
    print("   - قد يكون غير معتمد بالكامل")
    print("   - قد تحتاج لإعادة تقديمه")
    print()
    
except Exception as e:
    print(f"❌ خطأ في جلب تفاصيل الرسالة:")
    print(f"   {str(e)}")
    sys.exit(1)

print("=" * 80)
