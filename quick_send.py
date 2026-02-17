"""
اختبار سريع - إرسال مباشر بالقالب الأساسي
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

print("=" * 80)
print("⚡ إرسال سريع بالقالب الأساسي المجرّب")
print("=" * 80)
print()

# استخدام القالب الأساسي
CONTENT_SID = config['content_sid']

# بيانات المرسل إليه
TEST_NAME = "أ. باسم الحربي"
TEST_PHONE = "966554299950"  # الرقم الذي أدخلته

print(f"📋 معلومات الإرسال:")
print(f"   القالب: {config['template_name']}")
print(f"   Content SID: {CONTENT_SID}")
print(f"   الاسم: {TEST_NAME}")
print(f"   الرقم: +{TEST_PHONE}")
print()
print("⏳ جاري الإرسال...")
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # إرسال مباشر
    message = client.messages.create(
        content_sid=CONTENT_SID,
        content_variables=json.dumps({"1": TEST_NAME}),
        from_=FROM_PHONE,
        to=f"whatsapp:+{TEST_PHONE}"
    )
    
    print("=" * 80)
    print("✅ تم إرسال الدعوة بنجاح!")
    print("=" * 80)
    print()
    print(f"📋 تفاصيل الإرسال:")
    print(f"   Message SID: {message.sid}")
    print(f"   الحالة الأولية: {message.status}")
    print(f"   من: {message.from_}")
    print(f"   إلى: {message.to}")
    print(f"   الوقت: {message.date_created}")
    print()
    
    print("=" * 80)
    print("📱 التحقق من الرسالة:")
    print("=" * 80)
    print()
    print("1. افتح WhatsApp على رقم +966554299950")
    print("2. ابحث عن رسالة من +966550308539")
    print("3. يجب أن تظهر الدعوة مع أزرار تفاعلية")
    print()
    print("⏱️  انتظر 1-2 دقيقة ثم شغّل:")
    print("   python check_status.py")
    print()
    
    # حفظ Message SID للمتابعة
    with open("last_message.txt", "w") as f:
        f.write(message.sid)
    
    print("💾 تم حفظ Message SID في: last_message.txt")
    print()
    
except Exception as e:
    print("=" * 80)
    print(f"❌ خطأ في الإرسال:")
    print("=" * 80)
    print()
    print(f"   {str(e)}")
    print()
    
    if "63019" in str(e):
        print("⚠️ خطأ 63019: القالب مرفوض من WhatsApp")
        print()
        print("💡 الحلول:")
        print("   1. تحقق من اعتماد القالب في WhatsApp Business Manager")
        print("   2. قد يكون القالب تم تعطيله مؤقتاً")
        print("   3. جرّب قالباً آخر")
    elif "63016" in str(e):
        print("⚠️ خطأ 63016: القالب غير معتمد")
        print()
        print("💡 انتظر اعتماد القالب من WhatsApp")
    
    sys.exit(1)

print("=" * 80)
print("✅ تم!")
print("=" * 80)
