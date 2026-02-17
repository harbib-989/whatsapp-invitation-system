"""
فحص حالة القوالب المعتمدة
"""
import os
import sys
import json
from dotenv import load_dotenv
from twilio.rest import Client

# إصلاح ترميز الطرفية في Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

# إعدادات Twilio
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

# قراءة التكوين
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

print("=" * 70)
print("فحص حالة القوالب")
print("=" * 70)
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # فحص القالب الأساسي
    print("1️⃣ القالب الأساسي:")
    print(f"   الاسم: {config['template_name']}")
    print(f"   Content SID: {config['content_sid']}")
    
    try:
        content = client.content.v1.contents(config['content_sid']).fetch()
        print(f"   ✅ الحالة: موجود وصالح")
        print(f"   اللغة: {content.language}")
        print(f"   الاسم التعريفي: {content.friendly_name}")
        
        # عرض الأنواع المتاحة
        if hasattr(content, 'types'):
            print(f"   الأنواع المتاحة: {list(content.types.keys())}")
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
    
    print()
    
    # فحص قالب VIP
    if config.get('content_sid_vip_card'):
        print("2️⃣ قالب VIP Card:")
        print(f"   الاسم: {config.get('template_name_vip_card')}")
        print(f"   Content SID: {config['content_sid_vip_card']}")
        
        try:
            content_vip = client.content.v1.contents(config['content_sid_vip_card']).fetch()
            print(f"   ✅ الحالة: موجود وصالح")
            print(f"   اللغة: {content_vip.language}")
            print(f"   الاسم التعريفي: {content_vip.friendly_name}")
            
            if hasattr(content_vip, 'types'):
                print(f"   الأنواع المتاحة: {list(content_vip.types.keys())}")
        except Exception as e:
            print(f"   ❌ خطأ: {e}")
        
        print()
    
    # عرض معلومات الحساب
    print("📊 معلومات الحساب:")
    print(f"   نوع الحساب: {config.get('account_type', 'N/A')}")
    print(f"   اسم الأعمال: {config.get('business_name', 'N/A')}")
    print(f"   حالة المرسل: {config.get('sender_status', 'N/A')}")
    print(f"   تقييم الجودة: {config.get('quality_rating', 'N/A')}")
    print(f"   السرعة: {config.get('throughput', 'N/A')}")
    print()
    
    if config.get('note'):
        print(f"📝 ملاحظة: {config['note']}")
        print()
    
    print("✅ جميع القوالب جاهزة للإرسال!")
    
except Exception as e:
    print(f"❌ خطأ في الاتصال: {e}")
    sys.exit(1)

print()
print("=" * 70)
