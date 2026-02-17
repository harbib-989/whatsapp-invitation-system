import sys
import os
from dotenv import load_dotenv
from twilio.rest import Client
import json

# إعداد الترميز
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

print("=" * 70)
print("🔍 فحص جميع القوالب")
print("=" * 70)
print()

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

templates_to_check = [
    ("content_sid", "invite_20260207185112"),
    ("content_sid_vip", "template_name_vip"),
    ("content_sid_vip_card", "technicalcompetenciesforum")
]

try:
    client = Client(account_sid, auth_token)
    
    for sid_key, name in templates_to_check:
        content_sid = config.get(sid_key)
        if not content_sid:
            continue
            
        print(f"📋 القالب: {name}")
        print(f"SID: {content_sid}")
        print("-" * 70)
        
        try:
            content = client.content.v1.contents(content_sid).fetch()
            print(f"✅ الاسم: {content.friendly_name}")
            print(f"📝 النوع: {list(content.types.keys())[0] if content.types else 'Unknown'}")
            
            # تحقق من وجود صور
            for type_key, type_content in content.types.items():
                if isinstance(type_content, dict):
                    if 'media' in type_content and type_content['media']:
                        print(f"🖼️ يحتوي صورة: {type_content['media'][0][:60]}...")
                    else:
                        print("📝 نصي فقط (بدون صورة)")
                    
                    # عدد المتغيرات
                    body = type_content.get('body', '')
                    var_count = body.count('{{')
                    print(f"🔢 عدد المتغيرات: {var_count}")
            
            print()
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            print()

except Exception as e:
    print(f"❌ خطأ عام: {e}")
