"""
اختبار إرسال دعوة VIP Card بالصورة
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
print("🎉 اختبار قالب VIP Card مع الصورة")
print("=" * 80)
print()

# استخدام قالب VIP Card
CONTENT_SID = config.get('content_sid_vip_card')
TEMPLATE_NAME = config.get('template_name_vip_card')

if not CONTENT_SID:
    print("❌ خطأ: قالب VIP Card غير موجود في التكوين!")
    sys.exit(1)

print(f"📋 معلومات القالب:")
print(f"   الاسم: {TEMPLATE_NAME}")
print(f"   Content SID: {CONTENT_SID}")
print(f"   نوع القالب: VIP Card مع صورة ⭐")
print()

# طلب بيانات المدعو
print("📝 أدخل بيانات المدعو (اترك فارغاً لاستخدام بيانات تجريبية):")
print()

name = input("الاسم الكامل (مثل: سعادة الدكتور أحمد محمد العلي): ").strip()
if not name:
    name = "سعادة الدكتور أحمد محمد العلي"

phone = input("رقم الهاتف (مثال: 0501234567): ").strip()
if not phone:
    phone = "966568112166"  # رقمك من invitees.json
else:
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
print("-" * 80)
print(f"📱 سيتم إرسال دعوة VIP Card إلى:")
print(f"   الاسم: {name}")
print(f"   الرقم: +{phone}")
print(f"   القالب: VIP Card مع صورة ⭐")
print(f"   Content SID: {CONTENT_SID}")
print()
print("📌 المميزات:")
print("   ✅ بطاقة احترافية مع صورة مدمجة")
print("   ✅ أزرار تفاعلية (تأكيد/اعتذار)")
print("   ✅ تنسيق رسمي فاخر")
print("-" * 80)
print()

confirm = input("هل أنت متأكد من الإرسال؟ (نعم/لا): ").strip().lower()
if confirm not in ["نعم", "yes", "y", "ن"]:
    print("تم الإلغاء.")
    sys.exit(0)

print()
print("⏳ جاري الإرسال...")
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # إرسال باستخدام قالب VIP Card المعتمد
    message = client.messages.create(
        content_sid=CONTENT_SID,
        content_variables=json.dumps({"1": name}),
        from_=FROM_PHONE,
        to=f"whatsapp:+{phone}"
    )
    
    print("=" * 80)
    print("✅ تم إرسال دعوة VIP Card بنجاح!")
    print("=" * 80)
    print()
    print(f"📋 تفاصيل الإرسال:")
    print(f"   Message SID: {message.sid}")
    print(f"   الحالة: {message.status}")
    print(f"   من: {message.from_}")
    print(f"   إلى: {message.to}")
    print(f"   وقت الإرشاء: {message.date_created}")
    print()
    
    print("=" * 80)
    print("📱 افتح WhatsApp الآن!")
    print("=" * 80)
    print()
    print("يجب أن تشاهد:")
    print()
    print("┌─────────────────────────────────────┐")
    print("│  [صورة الدعوة - ملتقى الكفاءات]   │ ← الصورة مدمجة!")
    print("├─────────────────────────────────────┤")
    print("│                                     │")
    print("│  💼 دعوة رسمية                     │")
    print("│                                     │")
    print(f"│  المكرم {name[:20]}")
    print("│  حفظه الله                         │")
    print("│                                     │")
    print("│  يسر الكلية التقنية بالأحساء       │")
    print("│  أن تتشرف بدعوتكم الكريمة لحضور:  │")
    print("│                                     │")
    print("│  ملتقى الكفاءات التقنية            │")
    print("│                                     │")
    print("│  [✅ تأكيد الحضور] [❌ اعتذار]     │")
    print("│                                     │")
    print("└─────────────────────────────────────┘")
    print()
    print("🎉 دعوة VIP احترافية مع صورة مدمجة!")
    print()
    
    # حفظ سجل الإرسال
    log_entry = {
        "timestamp": message.date_created.isoformat() if message.date_created else "N/A",
        "name": name,
        "phone": phone,
        "message_sid": message.sid,
        "status": message.status,
        "template_type": "VIP Card",
        "content_sid": CONTENT_SID
    }
    
    log_file = "vip_card_test_log.json"
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
    print("=" * 80)
    print(f"❌ خطأ في الإرسال:")
    print("=" * 80)
    print()
    print(f"   {str(e)}")
    print()
    print("💡 تأكد من:")
    print("   1. صحة الرقم")
    print("   2. اتصال الإنترنت")
    print("   3. بيانات Twilio في ملف .env")
    print("   4. القالب معتمد من WhatsApp")
    print()
    
    # تفاصيل إضافية للمساعدة في التشخيص
    if "63016" in str(e):
        print("⚠️  الخطأ 63016: القالب غير معتمد أو Content SID غير صحيح")
        print("   الحل: تأكد من اعتماد القالب في WhatsApp Business Manager")
    
    sys.exit(1)

print("=" * 80)
