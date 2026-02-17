"""
فحص حالة آخر الرسائل المرسلة وتشخيص المشاكل
"""
import os
import sys
import json
from datetime import datetime, timedelta
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
FROM_PHONE = os.environ.get("TWILIO_FROM_PHONE", "whatsapp:+966550308539")

print("=" * 80)
print("🔍 فحص حالة الرسائل المرسلة")
print("=" * 80)
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    print("⏳ جاري جلب آخر 10 رسائل...")
    print()
    
    # جلب آخر 10 رسائل من آخر 24 ساعة
    messages = client.messages.list(
        from_=FROM_PHONE,
        date_sent_after=datetime.now() - timedelta(hours=24),
        limit=10
    )
    
    if not messages:
        print("❌ لا توجد رسائل مرسلة في آخر 24 ساعة")
        print()
        sys.exit(0)
    
    print(f"✅ تم العثور على {len(messages)} رسالة")
    print()
    print("=" * 80)
    
    for i, msg in enumerate(messages, 1):
        print()
        print(f"📨 رسالة #{i}")
        print("-" * 80)
        print(f"   Message SID: {msg.sid}")
        print(f"   إلى: {msg.to}")
        print(f"   من: {msg.from_}")
        print(f"   الحالة: {msg.status}")
        print(f"   وقت الإرسال: {msg.date_sent}")
        print(f"   وقت التحديث: {msg.date_updated}")
        
        # عرض حالة الرسالة بالتفصيل
        status_emoji = {
            'queued': '⏳ في قائمة الانتظار',
            'sending': '📤 جاري الإرسال',
            'sent': '✅ تم الإرسال',
            'delivered': '✅ تم التوصيل',
            'read': '✅ تم القراءة',
            'failed': '❌ فشل',
            'undelivered': '❌ لم يتم التوصيل'
        }
        
        status_text = status_emoji.get(msg.status, msg.status)
        print(f"   📊 الحالة التفصيلية: {status_text}")
        
        # إذا كان هناك خطأ
        if msg.error_code:
            print(f"   ⚠️ كود الخطأ: {msg.error_code}")
            print(f"   ⚠️ رسالة الخطأ: {msg.error_message}")
            
            # شرح الأخطاء الشائعة
            error_explanations = {
                '63007': 'القالب غير موجود أو تم حذفه',
                '63016': 'القالب غير معتمد من WhatsApp',
                '21211': 'رقم الهاتف غير صالح',
                '21408': 'المستلم لم يوافق على استقبال رسائل من حسابك',
                '63015': 'المتغيرات المطلوبة للقالب ناقصة أو خاطئة',
                '21610': 'الرسالة محظورة بسبب محتوى غير مناسب',
                '30007': 'تجاوز حد الإرسال (Rate Limit)',
            }
            
            if str(msg.error_code) in error_explanations:
                print(f"   💡 الشرح: {error_explanations[str(msg.error_code)]}")
        
        # السعر
        if msg.price:
            print(f"   💰 السعر: {msg.price} {msg.price_unit}")
        
        # نوع الرسالة
        if hasattr(msg, 'num_segments'):
            print(f"   📝 عدد الأجزاء: {msg.num_segments}")
        
        print("-" * 80)
    
    print()
    print("=" * 80)
    print("📊 ملخص الحالات:")
    print("=" * 80)
    
    # إحصائيات
    status_counts = {}
    for msg in messages:
        status_counts[msg.status] = status_counts.get(msg.status, 0) + 1
    
    for status, count in status_counts.items():
        emoji = status_emoji.get(status, status)
        print(f"   {emoji}: {count}")
    
    print()
    print("=" * 80)
    print("💡 معاني الحالات:")
    print("=" * 80)
    print("   queued       - في قائمة الانتظار (طبيعي في البداية)")
    print("   sending      - جاري الإرسال (قد يستغرق ثوانٍ)")
    print("   sent         - تم الإرسال من Twilio")
    print("   delivered    - تم التوصيل إلى WhatsApp")
    print("   read         - تم قراءة الرسالة")
    print("   failed       - فشل الإرسال (تحقق من سبب الخطأ)")
    print("   undelivered  - لم يتم التوصيل (المستلم غير متصل أو حظر)")
    print()
    
    # نصائح
    print("=" * 80)
    print("💡 نصائح:")
    print("=" * 80)
    
    # البحث عن مشاكل شائعة
    has_failed = any(msg.status == 'failed' for msg in messages)
    has_undelivered = any(msg.status == 'undelivered' for msg in messages)
    has_queued = any(msg.status == 'queued' for msg in messages)
    
    if has_failed:
        print("   ⚠️ يوجد رسائل فاشلة - راجع أكواد الأخطاء أعلاه")
    
    if has_undelivered:
        print("   ⚠️ رسائل لم تُوصل - قد يكون المستلم غير متصل أو حظر الحساب")
    
    if has_queued:
        print("   ⏳ رسائل في قائمة الانتظار - انتظر قليلاً ثم أعد الفحص")
    
    # نصائح عامة
    print()
    print("   1. إذا كانت الحالة 'queued' أو 'sending':")
    print("      - انتظر 1-2 دقيقة ثم أعد تشغيل هذا السكريبت")
    print()
    print("   2. إذا كانت الحالة 'failed' مع كود 63016:")
    print("      - القالب غير معتمد، راجع WhatsApp Business Manager")
    print()
    print("   3. إذا كانت الحالة 'undelivered':")
    print("      - تأكد من أن رقم المستلم صحيح")
    print("      - تحقق من أن المستلم لم يحظر الحساب")
    print("      - المستلم قد يكون غير متصل بالإنترنت")
    print()
    print("   4. للتحقق من رسالة معينة:")
    print("      - انسخ Message SID")
    print("      - ابحث عنه في Twilio Console للتفاصيل الكاملة")
    print()
    
    print("=" * 80)
    
except Exception as e:
    print(f"❌ خطأ في الاتصال بـ Twilio:")
    print(f"   {str(e)}")
    print()
    print("💡 تأكد من:")
    print("   1. بيانات Twilio صحيحة في ملف .env")
    print("   2. اتصال الإنترنت يعمل")
    sys.exit(1)

print()
print("=" * 80)
