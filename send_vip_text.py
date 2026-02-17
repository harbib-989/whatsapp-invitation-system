import json
import sys
import os
from dotenv import load_dotenv
from twilio.rest import Client
import time

# إعداد الترميز
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

# قراءة الإعدادات
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# بيانات Twilio
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_FROM_PHONE")

# Content SID للقالب VIP (نصي فقط - بدون صورة)
content_sid_vip = config["content_sid_vip"]

print("=" * 70)
print("🎯 اختبار القالب: job_fair_vip (نصي - بدون صورة)")
print("=" * 70)
print()
print(f"📋 Content SID: {content_sid_vip}")
print(f"📝 النوع: twilio/quick-reply (نصي)")
print(f"🔢 المتغيرات: 2 (الاسم + التخصص)")
print()

# بيانات الاختبار
test_name = "محمد أحمد"
test_major = "علوم الحاسب"
test_phone = "whatsapp:+966534058083"

print(f"📱 الإرسال إلى: {test_phone}")
print(f"👤 الاسم: {test_name}")
print(f"🎓 التخصص: {test_major}")
print()
print("⏳ جاري الإرسال...")
print()

try:
    client = Client(account_sid, auth_token)
    
    # إرسال الرسالة
    message = client.messages.create(
        from_=from_number,
        to=test_phone,
        content_sid=content_sid_vip,
        content_variables=json.dumps({
            "1": test_name,
            "2": test_major
        })
    )
    
    print("=" * 70)
    print("✅ تم الإرسال بنجاح!")
    print("=" * 70)
    print()
    print(f"📬 Message SID: {message.sid}")
    print(f"📊 Status: {message.status}")
    print()
    
    # حفظ SID
    with open("last_vip_message.txt", "w", encoding="utf-8") as f:
        f.write(message.sid)
    
    print("⏳ انتظر 20 ثانية للتحقق...")
    time.sleep(20)
    
    # التحقق من الحالة
    message = client.messages(message.sid).fetch()
    
    print()
    print("=" * 70)
    print("📊 حالة التسليم")
    print("=" * 70)
    print()
    print(f"الحالة: {message.status}")
    print(f"التاريخ: {message.date_sent}")
    
    if message.error_code:
        print()
        print("❌ يوجد خطأ!")
        print(f"رمز الخطأ: {message.error_code}")
        print(f"الرسالة: {message.error_message}")
    else:
        print()
        if message.status == "delivered":
            print("🎉 تم التسليم بنجاح - تحقق من جوالك!")
        elif message.status == "sent":
            print("📤 تم الإرسال - في طريقه إليك")
        else:
            print(f"📊 الحالة: {message.status}")
    
except Exception as e:
    print("=" * 70)
    print("❌ خطأ في الإرسال!")
    print("=" * 70)
    print()
    print(f"التفاصيل: {e}")
    sys.exit(1)
