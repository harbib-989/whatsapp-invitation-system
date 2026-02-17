"""
إرسال سريع بقالب VIP Card (مع صورة)
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
print("⭐ إرسال سريع بقالب VIP Card (مع صورة)")
print("=" * 80)
print()

# استخدام قالب VIP Card
CONTENT_SID = config.get('content_sid_vip_card')

if not CONTENT_SID:
    print("❌ قالب VIP Card غير موجود في التكوين!")
    print()
    print("Content SID المطلوب: HX0b25b1f0ba0489585725958a0db45ce1")
    sys.exit(1)

print(f"📋 معلومات القالب:")
print(f"   الاسم: {config.get('template_name_vip_card')}")
print(f"   Content SID: {CONTENT_SID}")
print(f"   المميزات: ⭐ بطاقة مع صورة مدمجة + أزرار تفاعلية")
print()

# بيانات المرسل إليه
TEST_NAME = "أ. باسم الحربي"
TEST_PHONE = "966554299950"

print(f"📱 معلومات الإرسال:")
print(f"   الاسم: {TEST_NAME}")
print(f"   الرقم: +{TEST_PHONE}")
print()
print("⏳ جاري إرسال الدعوة مع الصورة...")
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # أولاً: التحقق من حالة القالب
    print("🔍 التحقق من حالة القالب...")
    try:
        content = client.content.v1.contents(CONTENT_SID).fetch()
        print(f"   ✅ القالب موجود: {content.friendly_name}")
        print(f"   اللغة: {content.language}")
        if hasattr(content, 'types'):
            print(f"   الأنواع: {list(content.types.keys())}")
        print()
    except Exception as e:
        print(f"   ⚠️ تحذير: لم نتمكن من التحقق من القالب: {e}")
        print(f"   سنحاول الإرسال على أي حال...")
        print()
    
    # الإرسال
    print("📤 جاري الإرسال...")
    message = client.messages.create(
        content_sid=CONTENT_SID,
        content_variables=json.dumps({"1": TEST_NAME}),
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
    print(f"   الحالة الأولية: {message.status}")
    print(f"   من: {message.from_}")
    print(f"   إلى: {message.to}")
    print(f"   الوقت: {message.date_created}")
    print()
    
    print("=" * 80)
    print("📱 ماذا تتوقع في WhatsApp:")
    print("=" * 80)
    print()
    print("┌─────────────────────────────────────┐")
    print("│  [صورة ملتقى الكفاءات]             │ ← الصورة")
    print("├─────────────────────────────────────┤")
    print("│  💼 دعوة رسمية                     │")
    print("│                                     │")
    print("│  المكرم أ. باسم الحربي             │")
    print("│  حفظه الله                         │")
    print("│                                     │")
    print("│  يسر الكلية التقنية...             │")
    print("│                                     │")
    print("│  [✅ تأكيد الحضور] [❌ اعتذار]     │")
    print("└─────────────────────────────────────┘")
    print()
    
    print("⏱️  انتظر 30-60 ثانية ثم:")
    print("   1. افتح WhatsApp على +966554299950")
    print("   2. ابحث عن رسالة من +966550308539")
    print("   3. يجب أن ترى بطاقة مع صورة مدمجة")
    print()
    print("   أو شغّل: python check_status.py")
    print()
    
    # حفظ Message SID
    with open("last_vip_message.txt", "w") as f:
        f.write(f"{message.sid}\n")
        f.write(f"Name: {TEST_NAME}\n")
        f.write(f"Phone: +{TEST_PHONE}\n")
        f.write(f"Time: {message.date_created}\n")
    
    print("💾 تم حفظ تفاصيل الرسالة في: last_vip_message.txt")
    print()
    
except Exception as e:
    print()
    print("=" * 80)
    print(f"❌ خطأ في الإرسال:")
    print("=" * 80)
    print()
    print(f"   {str(e)}")
    print()
    
    # تشخيص الأخطاء
    error_str = str(e)
    
    if "63019" in error_str:
        print("⚠️ خطأ 63019: القالب مرفوض من WhatsApp")
        print()
        print("💡 السبب المحتمل:")
        print("   - قالب VIP Card غير معتمد بشكل كامل من WhatsApp")
        print("   - القالب يحتوي على محتوى أو صورة محظورة")
        print("   - نوع القالب (Card) قد لا يكون مدعوماً")
        print()
        print("✅ الحلول:")
        print("   1. تحقق من اعتماد القالب في WhatsApp Business Manager:")
        print("      https://business.facebook.com")
        print()
        print("   2. إذا كان القالب غير معتمد:")
        print("      - انتظر الاعتماد (15 دقيقة - 24 ساعة)")
        print("      - أو أعد تقديم القالب بصورة مختلفة")
        print()
        print("   3. استخدم القالب الأساسي (بدون صورة) حالياً:")
        print("      python quick_send.py")
        print()
        
    elif "63016" in error_str:
        print("⚠️ خطأ 63016: القالب غير معتمد")
        print()
        print("💡 القالب قيد المراجعة من WhatsApp")
        print("   - انتظر الاعتماد (عادةً 15 دقيقة - 24 ساعة)")
        print("   - تحقق من الحالة في WhatsApp Business Manager")
        print()
        
    elif "21211" in error_str:
        print("⚠️ خطأ 21211: رقم الهاتف غير صالح")
        print()
        
    else:
        print("💡 للمزيد من التفاصيل:")
        print("   - افتح Twilio Console: https://console.twilio.com")
        print("   - ابحث عن Message SID في الأعلى")
        print("   - راجع سجل الأخطاء التفصيلي")
        print()
    
    sys.exit(1)

print("=" * 80)
print("✅ تم!")
print("=" * 80)
