"""
فحص حالة رسالة معينة
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

# الرسالة التي تم إرسالها
MESSAGE_SID = "MMd4cd847e1b0cefba15de8dc7d133d4bc"

print("=" * 80)
print("🔍 فحص حالة رسالة VIP Card")
print("=" * 80)
print()
print(f"Message SID: {MESSAGE_SID}")
print()
print("⏳ جاري جلب الحالة...")
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages(MESSAGE_SID).fetch()
    
    print("=" * 80)
    print("📊 حالة الرسالة:")
    print("=" * 80)
    print()
    print(f"   الحالة: {message.status}")
    print(f"   إلى: {message.to}")
    print(f"   من: {message.from_}")
    print(f"   وقت الإرسال: {message.date_sent}")
    print(f"   وقت التحديث: {message.date_updated}")
    
    if message.error_code:
        print(f"   ⚠️ كود الخطأ: {message.error_code}")
        print(f"   ⚠️ رسالة الخطأ: {message.error_message}")
    
    print()
    
    # شرح الحالة
    status_info = {
        'queued': '⏳ في قائمة الانتظار - سيتم إرسالها قريباً',
        'sending': '📤 جاري الإرسال - انتظر قليلاً',
        'sent': '✅ تم الإرسال من Twilio',
        'delivered': '✅ تم التوصيل إلى WhatsApp - نجاح كامل!',
        'read': '✅ تم قراءة الرسالة - نجاح كامل!',
        'failed': '❌ فشل الإرسال',
        'undelivered': '❌ لم يتم التوصيل'
    }
    
    status_text = status_info.get(message.status, message.status)
    print(f"💡 التفسير: {status_text}")
    print()
    
    if message.status == 'queued':
        print("📌 الرسالة في قائمة الانتظار")
        print("   - انتظر 30-60 ثانية ثم أعد تشغيل هذا السكريبت")
        print("   - أو افتح WhatsApp للتحقق")
        
    elif message.status == 'sending':
        print("📌 جاري الإرسال")
        print("   - الرسالة في طريقها")
        print("   - انتظر 30 ثانية ثم تحقق من WhatsApp")
        
    elif message.status in ['sent', 'delivered', 'read']:
        print("=" * 80)
        print("🎉 نجح! الرسالة وصلت!")
        print("=" * 80)
        print()
        print("📱 افتح WhatsApp على +966554299950")
        print("   ابحث عن رسالة من +966550308539")
        print()
        print("✅ يجب أن ترى:")
        print("   - بطاقة مع صورة ملتقى الكفاءات")
        print("   - أزرار تفاعلية (تأكيد/اعتذار)")
        print("   - تصميم احترافي")
        
    elif message.status == 'failed':
        print("=" * 80)
        print("❌ فشل الإرسال")
        print("=" * 80)
        print()
        
        if message.error_code == 63019:
            print("⚠️ خطأ 63019: القالب مرفوض من WhatsApp")
            print()
            print("💡 السبب المحتمل:")
            print("   - قالب VIP Card غير معتمد بالكامل")
            print("   - الصورة قد تكون مخالفة")
            print("   - نوع القالب (Card) غير مدعوم")
            print()
            print("✅ الحل:")
            print("   استخدم القالب الأساسي (بدون صورة):")
            print("   python quick_send.py")
            
        elif message.error_code == 63016:
            print("⚠️ خطأ 63016: القالب غير معتمد")
            print("   انتظر اعتماد القالب من WhatsApp")
    
    print()
    print("=" * 80)
    
except Exception as e:
    print(f"❌ خطأ: {e}")
    sys.exit(1)

print()
