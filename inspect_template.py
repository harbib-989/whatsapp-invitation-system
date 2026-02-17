import sys
import os
from dotenv import load_dotenv
from twilio.rest import Client
import json

# إعداد الترميز
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# تحميل المتغيرات
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# قراءة Content SID
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

content_sid = config["content_sid_vip_card"]

print("=" * 70)
print("🔍 فحص تفاصيل القالب")
print("=" * 70)
print()
print(f"Content SID: {content_sid}")
print()

try:
    client = Client(account_sid, auth_token)
    
    # جلب بيانات القالب
    content = client.content.v1.contents(content_sid).fetch()
    
    print("📋 معلومات القالب:")
    print("=" * 70)
    print(f"اسم القالب: {content.friendly_name}")
    print(f"النوع: {content.types}")
    print(f"اللغة: {content.language}")
    print()
    
    # جلب ApprovalFetch
    approval = client.content.v1.contents(content_sid).approval_fetch().fetch()
    
    print("📊 حالة الموافقة:")
    print("=" * 70)
    print(f"WhatsApp Status: {approval.whatsapp_approval_status}")
    
    if hasattr(approval, 'whatsapp_rejection_reasons'):
        print()
        print("❌ أسباب الرفض:")
        print(approval.whatsapp_rejection_reasons)
    
    print()
    print("📝 متغيرات القالب:")
    print("=" * 70)
    
    # عرض محتوى القالب
    if hasattr(content, 'types'):
        content_types = content.types
        print(f"Types: {content_types}")
    
except Exception as e:
    print(f"❌ خطأ: {e}")
    import traceback
    traceback.print_exc()
