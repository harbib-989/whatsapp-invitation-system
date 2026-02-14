"""
إنشاء قالب الدعوة الرسمية للمسؤولين مع صورة
مثل القالب العام - يحتوي على صورة + أزرار تفاعلية
"""
import os
import sys
import json
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import requests as http_requests
except ImportError:
    print("❌ تثبيت: pip install requests")
    sys.exit(1)

ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

if not ACCOUNT_SID or not AUTH_TOKEN:
    print("❌ تأكد من إعداد TWILIO_ACCOUNT_SID و TWILIO_AUTH_TOKEN في .env")
    sys.exit(1)

# رابط الصورة - يجب أن يكون عاماً
IMAGE_URL = "https://raw.githubusercontent.com/harbib-989/whatsapp-invitation-system/main/job_fair_image.png"

# نص القالب الرسمي
BODY_TEXT = (
    "دعوة رسمية\n\n"
    "المكرم {{1}} {{2}} حفظه الله\n"
    "السلام عليكم ورحمة الله وبركاته\n\n"
    "يسر الكلية التقنية بالأحساء أن تتشرف بدعوتكم الكريمة لحضور:\n\n"
    "ملتقى الكفاءات التقنية\n\n"
    "📅 التاريخ: يوم الأحد 15\n"
    "⏰ المدة: يومان متتاليان\n"
    "📍 المكان: مسرح الكلية التقنية - الكلية التقنية بالأحساء\n\n"
    "حضوركم يسرنا ويشرفنا\n\n"
    "الكلية التقنية بالأحساء\n"
    "المؤسسة العامة للتدريب التقني والمهني"
)

def main():
    print("=" * 60)
    print("  إنشاء قالب الدعوة الرسمية (مع صورة)")
    print("=" * 60)

    template_data = {
        "friendly_name": "job_fair_vip_card_" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "language": "ar",
        "variables": {"1": "الاسم", "2": "المنصب"},
        "types": {
            "twilio/card": {
                "title": "دعوة رسمية - ملتقى الكفاءات التقنية",
                "subtitle": "",
                "body": BODY_TEXT,
                "media": [IMAGE_URL],
                "actions": [
                    {"type": "QUICK_REPLY", "title": "تأكيد الحضور", "id": "accept"},
                    {"type": "QUICK_REPLY", "title": "اعتذار", "id": "decline"}
                ]
            },
            "twilio/text": {
                "body": BODY_TEXT
            }
        }
    }

    try:
        resp = http_requests.post(
            "https://content.twilio.com/v1/Content",
            json=template_data,
            auth=(ACCOUNT_SID, AUTH_TOKEN)
        )

        if resp.status_code != 201:
            print(f"❌ خطأ: {resp.status_code}")
            print(resp.text)
            sys.exit(1)

        sid = resp.json().get("sid")
        print(f"\n✅ تم إنشاء القالب بنجاح!")
        print(f"\n📌 Content SID: {sid}")
        print(f"\nالخطوات التالية:")
        print("  1. اذهب إلى Twilio Console → Content")
        print("  2. اضغط Submit for Approval")
        print("  3. بعد الموافقة، أضف في config.json:")
        print(f'     "content_sid_vip": "{sid}"')
        print("\n⚠️ هذا يستبدل القالب الرسمي السابق في النظام")
        print("\n" + "=" * 60)
        return sid

    except Exception as e:
        print(f"❌ خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
