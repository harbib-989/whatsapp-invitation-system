"""
إنشاء قالب الدعوة الرسمية للمسؤولين وكبار الشخصيات
ينشئ Content Template في Twilio ثم تحتاج الموافقة من WhatsApp

بعد التشغيل:
1. احصل على Content SID من المخرجات
2. أضفه في config.json أو متغير CONTENT_SID_VIP على Render
3. انتظر موافقة WhatsApp (Twilio Console → Content → Submit)
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
    print("pip install requests")
    sys.exit(1)

ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

if not ACCOUNT_SID or not AUTH_TOKEN:
    print("❌ تأكد من تعيين TWILIO_ACCOUNT_SID و TWILIO_AUTH_TOKEN في .env")
    sys.exit(1)

# نص القالب الرسمي - متغير 1: الاسم، متغير 2: المنصب
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
    print("  إنشاء قالب الدعوة الرسمية للمسؤولين")
    print("=" * 60)

    template_data = {
        "friendly_name": "job_fair_vip_" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "language": "ar",
        "variables": {"1": "الاسم", "2": "المنصب"},
        "types": {
            "twilio/quick-reply": {
                "body": BODY_TEXT,
                "actions": [
                    {"title": "تاكيد الحضور", "id": "accept"},
                    {"title": "اعتذار", "id": "decline"}
                ]
            },
            "twilio/text": {
                "body": BODY_TEXT + "\n\nللرد اكتب تاكيد او اعتذار"
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
        print(f"\n📋 Content SID: {sid}")
        print(f"\nالخطوات التالية:")
        print("  1. اذهب إلى Twilio Console → Content → استخدم الرابط أعلاه")
        print("  2. اضغط Submit for Approval لإرسال القالب لموافقة WhatsApp")
        print("  3. بعد الموافقة، أضف في config.json:")
        print(f'     "content_sid_vip": "{sid}"')
        print("  4. أو على Render أضف متغير:")
        print(f"     CONTENT_SID_VIP={sid}")
        print("\n" + "=" * 60)
        return sid

    except Exception as e:
        print(f"❌ خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
