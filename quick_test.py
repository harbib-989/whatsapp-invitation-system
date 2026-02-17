"""
اختبار سريع لإرسال دعوة بالقالب الجديد
"""
import os
import sys
import json
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
FROM_PHONE = os.environ.get("TWILIO_FROM_PHONE", "whatsapp:+966550308539")

# قراءة التكوين
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

print("=" * 70)
print("اختبار سريع للقالب الجديد")
print("=" * 70)
print()

# استخدام القالب الأساسي
CONTENT_SID = config['content_sid']
TEMPLATE_NAME = config['template_name']

print(f"📋 معلومات القالب:")
print(f"   الاسم: {TEMPLATE_NAME}")
print(f"   Content SID: {CONTENT_SID}")
print(f"   معتمد: {'✅ نعم' if config.get('approved') else '⏳ قيد المراجعة'}")
print(f"   تاريخ الاعتماد: {config.get('approval_date', 'N/A')}")
print()

# بيانات اختبار
test_name = "ضيف اختبار"
test_phone = "966568112166"  # رقمك من invitees.json

print(f"📱 إرسال دعوة اختبار إلى:")
print(f"   الاسم: {test_name}")
print(f"   الرقم: +{test_phone}")
print()
print("⏳ جاري الإرسال...")
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # إرسال باستخدام القالب المعتمد
    message = client.messages.create(
        content_sid=CONTENT_SID,
        content_variables=json.dumps({"1": test_name}),
        from_=FROM_PHONE,
        to=f"whatsapp:+{test_phone}"
    )
    
    print("✅ تم إرسال الدعوة بنجاح!")
    print()
    print(f"📋 تفاصيل الإرسال:")
    print(f"   Message SID: {message.sid}")
    print(f"   الحالة: {message.status}")
    print(f"   من: {message.from_}")
    print(f"   إلى: {message.to}")
    print()
    
    # محاولة الحصول على مزيد من التفاصيل
    print("📊 معلومات إضافية:")
    print(f"   وقت الإنشاء: {message.date_created}")
    print(f"   السعر: {message.price} {message.price_unit}")
    if message.error_code:
        print(f"   ⚠️ كود الخطأ: {message.error_code}")
        print(f"   رسالة الخطأ: {message.error_message}")
    print()
    
    print("💡 افتح WhatsApp على رقمك لرؤية الدعوة!")
    print("   يجب أن تظهر مع أزرار تفاعلية (تأكيد/اعتذار)")
    print()
    
except Exception as e:
    print(f"❌ خطأ في الإرسال:")
    print(f"   {str(e)}")
    print()
    
    # تفاصيل إضافية للمساعدة في التشخيص
    if "20003" in str(e):
        print("💡 الخطأ: مشكلة في المصادقة - تحقق من ACCOUNT_SID و AUTH_TOKEN")
    elif "21211" in str(e):
        print("💡 الخطأ: رقم الهاتف غير صالح")
    elif "63016" in str(e):
        print("💡 الخطأ: القالب غير معتمد أو غير موجود")
    
    sys.exit(1)

print("=" * 70)
