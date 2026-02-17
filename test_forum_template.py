import json
import sys
from twilio.rest import Client
from dotenv import load_dotenv
import os

# إعداد الترميز
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# تحميل المتغيرات من .env
load_dotenv()

# قراءة الإعدادات
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# بيانات Twilio
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
from_number = os.environ.get("FROM_WHATSAPP_NUMBER")

# Content SID للقالب الجديد
content_sid_forum = config["content_sid_vip_card"]  # القالب الجديد
template_name = config.get("template_name_forum", "technicalcompetenciesforum")

print("=" * 60)
print("🎯 اختبار القالب: technicalcompetenciesforum")
print("=" * 60)
print()
print(f"Content SID: {content_sid_forum}")
print(f"Template Name: {template_name}")
print()

if not all([account_sid, auth_token, from_number]):
    print("❌ خطأ: المتغيرات البيئية غير موجودة!")
    print("تأكد من وجود:")
    print("  - TWILIO_ACCOUNT_SID")
    print("  - TWILIO_AUTH_TOKEN")
    print("  - FROM_WHATSAPP_NUMBER")
    sys.exit(1)

# بيانات الاختبار
test_name = "محمد أحمد"
test_phone = "+966534058083"

print(f"📱 الإرسال إلى: {test_phone}")
print(f"👤 الاسم: {test_name}")
print()

try:
    client = Client(account_sid, auth_token)
    
    # إرسال الرسالة
    message = client.messages.create(
        from_=from_number,
        to=test_phone,
        content_sid=content_sid_forum,
        content_variables=json.dumps({
            "1": test_name
        })
    )
    
    print(f"✅ تم الإرسال بنجاح!")
    print()
    print(f"Message SID: {message.sid}")
    print(f"Status: {message.status}")
    print()
    print("=" * 60)
    print("⏱️ انتظر 10 ثوانٍ للتحقق من الحالة...")
    print("=" * 60)
    
    # حفظ SID للتحقق لاحقاً
    with open("last_forum_message.txt", "w", encoding="utf-8") as f:
        f.write(message.sid)
    
except Exception as e:
    print(f"❌ خطأ في الإرسال: {e}")
    sys.exit(1)
