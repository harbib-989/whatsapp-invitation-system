import json
import sys
import os
from dotenv import load_dotenv
from twilio.rest import Client

# إعداد الترميز
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# تحميل المتغيرات من .env
load_dotenv()

# قراءة الإعدادات
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# بيانات Twilio
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_FROM_PHONE")

# Content SID للقالب الجديد
content_sid_forum = config["content_sid_vip_card"]
template_name = config.get("template_name_forum", "technicalcompetenciesforum")

print("=" * 70)
print("🎯 إرسال دعوة منتدى الكفايات التقنية")
print("=" * 70)
print()
print(f"📋 Content SID: {content_sid_forum}")
print(f"📋 Template Name: {template_name}")
print(f"📋 Status: ✅ Approved by WhatsApp")
print()

# بيانات الاختبار
test_name = "محمد أحمد"
test_phone = "whatsapp:+966534058083"  # ← إضافة بادئة whatsapp:

print(f"📱 الإرسال إلى: {test_phone}")
print(f"👤 الاسم: {test_name}")
print(f"📞 من: {from_number}")
print()
print("⏳ جاري الإرسال...")
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
    
    print("=" * 70)
    print("✅ تم الإرسال بنجاح!")
    print("=" * 70)
    print()
    print(f"📬 Message SID: {message.sid}")
    print(f"📊 Status: {message.status}")
    print()
    
    # حفظ SID
    with open("last_forum_message.txt", "w", encoding="utf-8") as f:
        f.write(message.sid)
    
    print("=" * 70)
    print("⏱️ سأنتظر 20 ثانية ثم أتحقق من حالة التسليم...")
    print("=" * 70)
    print()
    print("✉️ تحقق من جوالك الآن!")
    
except Exception as e:
    print("=" * 70)
    print("❌ خطأ في الإرسال!")
    print("=" * 70)
    print()
    print(f"التفاصيل: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
