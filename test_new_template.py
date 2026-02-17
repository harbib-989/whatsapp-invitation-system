"""
اختبار إرسال دعوة بالقالب الجديد
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
print("اختبار إرسال دعوة بالقالب الجديد")
print("=" * 70)
print()
print("القوالب المتاحة:")
print(f"  1. القالب الأساسي: {config['template_name']}")
print(f"     Content SID: {config['content_sid']}")
print(f"     معتمد: {'✅ نعم' if config.get('approved') else '⏳ قيد المراجعة'}")
print()
print(f"  2. قالب VIP: {config.get('template_name_vip_card', 'غير متوفر')}")
if config.get('content_sid_vip_card'):
    print(f"     Content SID: {config['content_sid_vip_card']}")
    print(f"     معتمد: ✅ نعم")
print()
print("-" * 70)

# اختيار القالب
choice = input("اختر القالب (1 للأساسي، 2 لـ VIP): ").strip()
if choice == "2" and config.get('content_sid_vip_card'):
    CONTENT_SID = config['content_sid_vip_card']
    template_type = "VIP Card"
else:
    CONTENT_SID = config['content_sid']
    template_type = "أساسي"

print()
print(f"القالب المختار: {template_type}")
print(f"Content SID: {CONTENT_SID}")
print()

# طلب بيانات المدعو
name = input("اسم المدعو (اتركه فارغاً لاستخدام 'ضيف كريم'): ").strip()
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
print(f"  القالب: {template_type}")
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
    print(f"   القالب: {template_type}")
    print(f"   Content SID: {CONTENT_SID}")
    print()
    print("💡 افتح WhatsApp على رقم المدعو لرؤية الدعوة مع الأزرار التفاعلية!")
    print()
    
    # حفظ سجل الإرسال
    log_entry = {
        "timestamp": message.date_created.isoformat() if message.date_created else "N/A",
        "name": name,
        "phone": phone,
        "message_sid": message.sid,
        "status": message.status,
        "template_type": template_type,
        "content_sid": CONTENT_SID
    }
    
    # إضافة السجل إلى ملف
    log_file = "send_test_log.json"
    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    
    logs.append(log_entry)
    
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    print(f"📝 تم حفظ سجل الإرسال في: {log_file}")
    print()
    
except Exception as e:
    print(f"❌ خطأ في الإرسال:")
    print(f"   {str(e)}")
    print()
    print("💡 تأكد من:")
    print("   1. صحة الرقم")
    print("   2. اتصال الإنترنت")
    print("   3. بيانات Twilio في ملف .env")
    print("   4. القالب معتمد من WhatsApp")
    sys.exit(1)

print("=" * 70)
