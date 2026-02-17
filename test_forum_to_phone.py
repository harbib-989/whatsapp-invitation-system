"""
اختبار إرسال قالب technicalcompetenciesforum (منتدى الكفايات التقنية) إلى واتساب.
الاستخدام:
  python test_forum_to_phone.py
  python test_forum_to_phone.py 966501234567
  python test_forum_to_phone.py 0501234567
"""
import json
import sys
import os
import re
from dotenv import load_dotenv
from twilio.rest import Client

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_FROM_PHONE")

content_sid = config["content_sid_vip_card"]
template_name = config.get("template_name_forum", "technicalcompetenciesforum")

def normalize_phone(raw):
    """تحويل الرقم إلى صيغة 966xxxxxxxxx ثم whatsapp:+966..."""
    s = re.sub(r"\D", "", raw)
    if s.startswith("966"):
        pass
    elif s.startswith("0"):
        s = "966" + s[1:]
    elif len(s) == 9 and s.startswith("5"):
        s = "966" + s
    else:
        s = "966" + s
    return "whatsapp:+" + s

def main():
    print("=" * 70)
    print("🎯 اختبار القالب: technicalcompetenciesforum → واتساب")
    print("=" * 70)
    print()
    print(f"📋 Content SID: {content_sid}")
    print(f"📋 Template: {template_name}")
    print(f"📋 من: {from_number}")
    print()

    if len(sys.argv) >= 2:
        raw_phone = sys.argv[1]
    else:
        raw_phone = input("أدخل رقم الجوال (مثال: 966501234567 أو 0501234567): ").strip()
        if not raw_phone:
            raw_phone = "966534058083"
            print(f"استخدام الرقم الافتراضي: {raw_phone}")

    to_whatsapp = normalize_phone(raw_phone)
    test_name = "محمد أحمد"

    print()
    print(f"📱 الإرسال إلى: {to_whatsapp}")
    print(f"👤 الاسم في القالب: {test_name}")
    print()
    print("⏳ جاري الإرسال...")
    print()

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            from_=from_number,
            to=to_whatsapp,
            content_sid=content_sid,
            content_variables=json.dumps({"1": test_name}),
        )
        print("=" * 70)
        print("✅ تم الإرسال بنجاح!")
        print("=" * 70)
        print()
        print(f"📬 Message SID: {message.sid}")
        print(f"📊 Status: {message.status}")
        print()
        with open("last_forum_message.txt", "w", encoding="utf-8") as f:
            f.write(message.sid)
        print("✉️ تحقق من واتساب على الجوال.")
        return 0
    except Exception as e:
        print("=" * 70)
        print("❌ خطأ في الإرسال!")
        print("=" * 70)
        print()
        print(f"التفاصيل: {e}")
        print()
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
