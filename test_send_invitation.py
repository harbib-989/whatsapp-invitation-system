"""
اختبار إرسال دعوة واحدة مباشرة
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

# القالب المعتمد
CONTENT_SID = "HX5f92c7470551312f6d1d461f16dafdb6"

print("=" * 70)
print("اختبار إرسال دعوة تجريبية")
print("=" * 70)
print()

# طلب بيانات المدعو
name = input("اسم المدعو: ").strip()
if not name:
    name = "ضيف كريم"

phone = input("رقم الهاتف (مثال: 0501234567): ").strip()
if not phone:
    print("❌ يجب إدخال رقم الهاتف!")
    sys.exit(1)

# تنسيق الرقم
phone = "".join(c for c in phone if c.isdigit())
if phone.startswith("05") and len(phone) == 10:
    phone = "966" + phone[1:]
elif phone.startswith("5") and len(phone) == 9:
    phone = "966" + phone
elif phone.startswith("00966"):
    phone = phone[2:]

if len(phone) != 12 or not phone.startswith("966"):
    print("❌ رقم الهاتف غير صحيح!")
    print(f"   الرقم المُدخل: {phone}")
    sys.exit(1)

print()
print("-" * 70)
print(f"سيتم إرسال الدعوة إلى:")
print(f"  الاسم: {name}")
print(f"  الرقم: +{phone}")
print("-" * 70)
print()

confirm = input("هل أنت متأكد؟ (نعم/لا): ").strip().lower()
if confirm not in ["نعم", "yes", "y", "ن"]:
    print("تم الإلغاء.")
    sys.exit(0)

print()
print("جاري الإرسال...")
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # إرسال باستخدام القالب المعتمد
    message = client.messages.create(
        content_sid=CONTENT_SID,
        content_variables=json.dumps({"1": name}),
        from_=FROM_PHONE,
        to=f"whatsapp:+{phone}"
    )
    
    print("✅ تم إرسال الدعوة بنجاح!")
    print()
    print(f"📋 تفاصيل الإرسال:")
    print(f"   Message SID: {message.sid}")
    print(f"   الحالة: {message.status}")
    print(f"   من: {message.from_}")
    print(f"   إلى: {message.to}")
    print()
    print("💡 افتح WhatsApp على رقم المدعو لرؤية الدعوة مع الأزرار التفاعلية!")
    print()
    
except Exception as e:
    print(f"❌ خطأ في الإرسال:")
    print(f"   {str(e)}")
    print()
    print("💡 تأكد من:")
    print("   1. صحة الرقم")
    print("   2. اتصال الإنترنت")
    print("   3. بيانات Twilio في ملف .env")
    sys.exit(1)

print("=" * 70)
