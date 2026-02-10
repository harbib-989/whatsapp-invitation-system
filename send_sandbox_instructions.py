"""
إرسال تعليمات الانضمام للـ Sandbox لمجموعة من الأشخاص
"""
import os
import sys
import time
from dotenv import load_dotenv
from twilio.rest import Client

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
FROM_PHONE = os.environ.get("TWILIO_FROM_PHONE", "whatsapp:+966550308539")

print("=" * 70)
print("إرسال تعليمات الانضمام للـ Sandbox")
print("=" * 70)
print()

print("⚠️ مهم: قبل البدء")
print()
print("1. افتح: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
print("2. انسخ المعلومات التالية:")
print("   • رقم Sandbox (مثل: +1 415 523 8886)")
print("   • كود الانضمام (مثل: join happy-dog)")
print()
print("-" * 70)
print()

# إدخال معلومات Sandbox
sandbox_number = input("رقم Sandbox (اضغط Enter للتخطي): ").strip()
sandbox_code = input("كود الانضمام (اضغط Enter للتخطي): ").strip()

print()
print("-" * 70)
print()

# قائمة المدعوين
print("أدخل أرقام المدعوين (رقم واحد في كل سطر)")
print("اضغط Enter مرتين عند الانتهاء:")
print()

recipients = []
while True:
    phone = input("رقم هاتف (أو Enter للإنهاء): ").strip()
    if not phone:
        break
    
    name = input(f"  اسم صاحب الرقم {phone}: ").strip()
    
    # تنسيق الرقم
    phone_clean = "".join(c for c in phone if c.isdigit())
    if phone_clean.startswith("05") and len(phone_clean) == 10:
        phone_clean = "966" + phone_clean[1:]
    elif phone_clean.startswith("5") and len(phone_clean) == 9:
        phone_clean = "966" + phone_clean
    
    recipients.append({
        "name": name if name else "ضيف",
        "phone": phone_clean
    })
    print(f"  ✅ تم إضافة: {name if name else 'ضيف'} (+{phone_clean})")
    print()

if not recipients:
    print("❌ لم تُدخل أي أرقام!")
    sys.exit(0)

print()
print("-" * 70)
print()
print(f"📊 سيتم إرسال التعليمات إلى {len(recipients)} شخص")
print()

# إنشاء رسالة التعليمات
if sandbox_number and sandbox_code:
    instructions_message = f"""مرحباً {{name}} 👋

للحصول على دعوات الفعاليات من الكلية التقنية بالأحساء عبر WhatsApp:

📍 خطوات بسيطة:

1. أضف هذا الرقم لجهات الاتصال:
   {sandbox_number}

2. أرسل له هذه الرسالة بالضبط:
   {sandbox_code}

3. انتظر رسالة التأكيد

4. بعدها ستصلك الدعوات تلقائياً مع أزرار تفاعلية! ✅

شكراً
الكلية التقنية بالأحساء"""
else:
    instructions_message = """مرحباً {name} 👋

للحصول على دعوات الفعاليات من الكلية التقنية بالأحساء عبر WhatsApp:

📍 خطوات بسيطة:

1. أضف الرقم الذي سنرسله لك
2. أرسل له الكود المحدد
3. انتظر رسالة التأكيد
4. بعدها ستصلك الدعوات تلقائياً ✅

سنرسل لك التفاصيل قريباً

شكراً
الكلية التقنية بالأحساء"""

print("📝 معاينة الرسالة:")
print()
print("-" * 70)
print(instructions_message.format(name="[اسم المدعو]"))
print("-" * 70)
print()

confirm = input("هل تريد إرسال التعليمات؟ (نعم/لا): ").strip().lower()

if confirm not in ["نعم", "yes", "y", "ن"]:
    print("تم الإلغاء.")
    sys.exit(0)

print()
print("=" * 70)
print("جاري الإرسال...")
print("=" * 70)
print()

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    success_count = 0
    failed_count = 0
    
    for i, recipient in enumerate(recipients, 1):
        name = recipient["name"]
        phone = recipient["phone"]
        
        print(f"[{i}/{len(recipients)}] إرسال إلى: {name} (+{phone})...", end=" ")
        
        try:
            # إرسال رسالة SMS عادية (ليست WhatsApp)
            # لأن المستقبل لم ينضم بعد
            message = client.messages.create(
                body=instructions_message.format(name=name),
                from_=FROM_PHONE.replace("whatsapp:", ""),  # استخدام SMS
                to=f"+{phone}"
            )
            
            print(f"✅ تم ({message.sid})")
            success_count += 1
            
        except Exception as e:
            print(f"❌ فشل: {str(e)}")
            failed_count += 1
        
        # تأخير بين الرسائل
        if i < len(recipients):
            time.sleep(1)
    
    print()
    print("=" * 70)
    print("📊 النتائج:")
    print("=" * 70)
    print()
    print(f"✅ نجح: {success_count}/{len(recipients)}")
    print(f"❌ فشل: {failed_count}/{len(recipients)}")
    print()
    
    if success_count > 0:
        print("💡 الخطوات التالية:")
        print()
        print("1. انتظر حتى يقوم المدعوون بالانضمام")
        print(f"   (إرسال: {sandbox_code if sandbox_code else 'الكود'} إلى {sandbox_number if sandbox_number else 'رقم Sandbox'})")
        print()
        print("2. بعد انضمامهم، يمكنك إرسال الدعوات الفعلية:")
        print("   python webhook_server.py")
        print("   ثم: http://localhost:5000/dashboard")
        print()
        print("3. استخدم 'الإرسال الجماعي' لإرسال الدعوات لهم جميعاً!")
        print()

except Exception as e:
    print(f"❌ خطأ عام: {str(e)}")

print("=" * 70)
