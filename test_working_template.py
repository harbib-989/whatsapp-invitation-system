"""
اختبار إرسال بالقالب الأساسي المجرّب (الذي نجح سابقاً)
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
print("✅ اختبار بالقالب الأساسي المجرّب")
print("=" * 80)
print()

# استخدام القالب الأساسي الذي نجح في الرسالة MMeaa601a706a31e115587b9a7d0858fb1
CONTENT_SID = config['content_sid']  # HX3f0e4a3d084e11732b364230057c64aa

print(f"📋 معلومات القالب:")
print(f"   الاسم: {config['template_name']}")
print(f"   Content SID: {CONTENT_SID}")
print(f"   الحالة: ✅ مُجرّب ونجح سابقاً")
print()
print(f"✅ هذا القالب نجح في إرسال رسالتين تم قراءتهما:")
print(f"   - MMeaa601a706a31e115587b9a7d0858fb1 (17:53)")
print(f"   - MM771c4b05e2412bd18214630c996bb166 (17:38)")
print()

# بيانات اختبار
name = input("اسم المدعو (أو اضغط Enter لـ 'ضيف كريم'): ").strip()
if not name:
    name = "ضيف كريم"

phone = input("رقم الهاتف (أو اضغط Enter لرقمك المحفوظ): ").strip()
if not phone:
    phone = "966568112166"
else:
    phone = "".join(c for c in phone if c.isdigit())
    if phone.startswith("05") and len(phone) == 10:
        phone = "966" + phone[1:]
    elif phone.startswith("5") and len(phone) == 9:
        phone = "966" + phone

if len(phone) != 12 or not phone.startswith("966"):
    print("❌ رقم الهاتف غير صحيح!")
    sys.exit(1)

print()
print("-" * 80)
print(f"📱 سيتم إرسال الدعوة إلى:")
print(f"   الاسم: {name}")
print(f"   الرقم: +{phone}")
print(f"   القالب: الأساسي (مُجرّب) ✅")
print("-" * 80)
print()

confirm = input("هل تريد المتابعة؟ (نعم/لا): ").strip().lower()
if confirm not in ["نعم", "yes", "y", "ن"]:
    print("تم الإلغاء.")
    sys.exit(0)

print()
print("⏳ جاري الإرسال بالقالب المجرّب...")
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # إرسال باستخدام القالب الأساسي المجرّب
    message = client.messages.create(
        content_sid=CONTENT_SID,
        content_variables=json.dumps({"1": name}),
        from_=FROM_PHONE,
        to=f"whatsapp:+{phone}"
    )
    
    print("=" * 80)
    print("✅ تم إرسال الدعوة بنجاح!")
    print("=" * 80)
    print()
    print(f"📋 تفاصيل الإرسال:")
    print(f"   Message SID: {message.sid}")
    print(f"   الحالة: {message.status}")
    print(f"   من: {message.from_}")
    print(f"   إلى: {message.to}")
    print(f"   وقت الإرسال: {message.date_created}")
    print()
    
    print("💡 انتظر 30 ثانية ثم تحقق من:")
    print("   1. WhatsApp على رقمك")
    print("   2. تشغيل: python check_status.py")
    print()
    
    print("📊 ملاحظة:")
    print("   هذا القالب نجح سابقاً، لذا من المفترض أن يصل بدون مشاكل")
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
        print("💡 هذا غريب لأن نفس القالب نجح سابقاً!")
        print("   قد يكون:")
        print("   1. القالب تم تعطيله مؤخراً")
        print("   2. مشكلة مؤقتة في WhatsApp")
        print("   3. تجاوز حد الإرسال")
    
    sys.exit(1)

print("=" * 80)
