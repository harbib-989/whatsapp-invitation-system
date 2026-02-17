import sys
import os
from dotenv import load_dotenv
from twilio.rest import Client
import time

# إعداد الترميز
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# تحميل المتغيرات
load_dotenv()

# قراءة SID
with open("last_forum_message.txt", "r", encoding="utf-8") as f:
    message_sid = f.read().strip()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

print("⏳ انتظار 20 ثانية...")
time.sleep(20)
print()
print("=" * 70)
print(f"🔍 التحقق من Message SID: {message_sid}")
print("=" * 70)
print()

try:
    client = Client(account_sid, auth_token)
    message = client.messages(message_sid).fetch()
    
    print(f"📊 الحالة: {message.status}")
    print(f"📅 التاريخ: {message.date_sent}")
    print(f"💰 السعر: {message.price} {message.price_unit}")
    print()
    
    if message.error_code:
        print("=" * 70)
        print("❌ يوجد خطأ!")
        print("=" * 70)
        print()
        print(f"رمز الخطأ: {message.error_code}")
        print(f"رسالة الخطأ: {message.error_message}")
    else:
        print("=" * 70)
        print("✅ لا يوجد أخطاء - الرسالة في الطريق!")
        print("=" * 70)
        print()
        if message.status == "delivered":
            print("🎉 تم التسليم بنجاح!")
        elif message.status == "sent":
            print("📤 تم الإرسال - بانتظار التسليم")
        elif message.status == "queued":
            print("⏳ في قائمة الانتظار")
        else:
            print(f"📊 الحالة: {message.status}")
    
except Exception as e:
    print(f"❌ خطأ في الاستعلام: {e}")
