"""
إرسال سريع بقالب VIP Card (مع متغيرين صحيحين)
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
print("⭐ إرسال دعوة VIP Card (مصحح - مع متغيرين)")
print("=" * 80)
print()

# استخدام قالب VIP Card
CONTENT_SID = config.get('content_sid_vip_card')

if not CONTENT_SID:
    print("❌ قالب VIP Card غير موجود في التكوين!")
    sys.exit(1)

print(f"📋 معلومات القالب:")
print(f"   الاسم: {config.get('template_name_vip_card')}")
print(f"   Content SID: {CONTENT_SID}")
print(f"   الحالة: ✅ معتمد من WhatsApp")
print(f"   المتغيرات: {{1}} الاسم، {{2}} المنصب")
print()

# بيانات المرسل إليه
TEST_NAME = "أ. باسم الحربي"
TEST_POSITION = "مدير"  # ← المتغير الثاني المطلوب!
TEST_PHONE = "966554299950"

print(f"📱 معلومات الإرسال:")
print(f"   الاسم (متغير 1): {TEST_NAME}")
print(f"   المنصب (متغير 2): {TEST_POSITION}")
print(f"   الرقم: +{TEST_PHONE}")
print()
print("⏳ جاري الإرسال مع المتغيرين الصحيحين...")
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # الإرسال مع المتغيرين
    message = client.messages.create(
        content_sid=CONTENT_SID,
        content_variables=json.dumps({
            "1": TEST_NAME,      # المتغير الأول: الاسم
            "2": TEST_POSITION   # المتغير الثاني: المنصب ← هذا كان ناقصاً!
        }),
        from_=FROM_PHONE,
        to=f"whatsapp:+{TEST_PHONE}"
    )
    
    print()
    print("=" * 80)
    print("✅ تم إرسال الدعوة!")
    print("=" * 80)
    print()
    print(f"📋 تفاصيل الإرسال:")
    print(f"   Message SID: {message.sid}")
    print(f"   الحالة: {message.status}")
    print(f"   من: {message.from_}")
    print(f"   إلى: {message.to}")
    print(f"   الوقت: {message.date_created}")
    print()
    
    print("=" * 80)
    print("📱 ماذا تتوقع في WhatsApp:")
    print("=" * 80)
    print()
    print("┌─────────────────────────────────────────────┐")
    print("│                                             │")
    print("│  [صورة ملتقى الكفاءات التقنية]            │ ← الصورة")
    print("│                                             │")
    print("├─────────────────────────────────────────────┤")
    print("│  💼 دعوة رسمية - ملتقى الكفاءات التقنية   │")
    print("│                                             │")
    print("│  دعوة رسمية                                │")
    print("│                                             │")
    print(f"│  المكرم {TEST_NAME} {TEST_POSITION} حفظه الله        │")
    print("│  السلام عليكم ورحمة الله وبركاته          │")
    print("│                                             │")
    print("│  يسر الكلية التقنية بالأحساء              │")
    print("│  أن تتشرف بدعوتكم الكريمة لحضور:          │")
    print("│                                             │")
    print("│  ملتقى الكفاءات التقنية                    │")
    print("│                                             │")
    print("│  📅 التاريخ: يوم الأحد 15                  │")
    print("│  ⏰ المدة: يومان متتاليان                  │")
    print("│  📍 المكان: مسرح الكلية التقنية           │")
    print("│                                             │")
    print("│  حضوركم يسرنا ويشرفنا                     │")
    print("│                                             │")
    print("│  [✅ تاكيد الحضور] [❌ اعتذار]            │")
    print("│                                             │")
    print("│  الكلية التقنية بالأحساء                  │")
    print("│  المؤسسة العامة للتدريب التقني والمهني   │")
    print("└─────────────────────────────────────────────┘")
    print()
    
    print("⏱️  انتظر 30 ثانية ثم:")
    print("   1. افتح WhatsApp على +966554299950")
    print("   2. ابحث عن رسالة من +966550308539")
    print("   3. يجب أن ترى بطاقة احترافية مع صورة مدمجة!")
    print()
    print("   أو شغّل: python check_status.py")
    print()
    
    # حفظ Message SID
    print(f"💾 Message SID: {message.sid}")
    print()
    
except Exception as e:
    print()
    print("=" * 80)
    print(f"❌ خطأ في الإرسال:")
    print("=" * 80)
    print()
    print(f"   {str(e)}")
    print()
    
    if "63019" in str(e):
        print("⚠️ خطأ 63019: لا يزال هناك مشكلة")
        print()
        print("قد يكون السبب:")
        print("   - مشكلة في الصورة")
        print("   - قيود على نوع القالب (Card)")
        print("   - مشكلة في حساب WhatsApp Business")
        
    sys.exit(1)

print("=" * 80)
print("🎉 تم!")
print("=" * 80)
