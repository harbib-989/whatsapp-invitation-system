"""
فحص حالة الرسالة الأخيرة
"""
import os
import sys
import time
from dotenv import load_dotenv
from twilio.rest import Client

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

MESSAGE_SID = "MM32d60edb27ff2d0402e8bb5e35cf4cb0"

print("⏳ انتظار 30 ثانية...")
time.sleep(30)

print()
print("🔍 فحص الحالة...")
print()

client = Client(os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
msg = client.messages(MESSAGE_SID).fetch()

print("=" * 80)
print("📊 حالة رسالة VIP Card:")
print("=" * 80)
print()
print(f"   الحالة: {msg.status}")
if msg.error_code:
    print(f"   ⚠️ كود الخطأ: {msg.error_code}")
print()

status_map = {
    'queued': '⏳ في الانتظار',
    'sending': '📤 جاري الإرسال',
    'sent': '✅ تم الإرسال',
    'delivered': '✅✅ تم التوصيل - نجاح كامل!',
    'read': '✅✅✅ تم القراءة - نجاح كامل!',
    'failed': '❌ فشل',
    'undelivered': '❌ لم يوصل'
}

print(f"💡 {status_map.get(msg.status, msg.status)}")
print()

if msg.status in ['delivered', 'read']:
    print("=" * 80)
    print("🎉🎉🎉 نجح! الدعوة وصلت مع الصورة!")
    print("=" * 80)
    print()
    print("📱 افتح WhatsApp الآن وستجد:")
    print("   ✅ بطاقة احترافية")
    print("   ✅ صورة ملتقى الكفاءات مدمجة")
    print("   ✅ أزرار تفاعلية (تأكيد/اعتذار)")
    print()
elif msg.status == 'failed':
    print("❌ فشل - خطأ", msg.error_code)
else:
    print("⏳ لا تزال في الانتظار - أعد المحاولة بعد دقيقة")

print("=" * 80)
