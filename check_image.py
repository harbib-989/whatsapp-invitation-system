"""
التحقق من توفر الصورة على Render
"""
import sys
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

IMAGE_URL = "https://whatsapp-invitation-system.onrender.com/media/job_fair_image.png"

print("=" * 80)
print("🔍 التحقق من توفر الصورة")
print("=" * 80)
print()
print(f"الرابط: {IMAGE_URL}")
print()
print("⏳ جاري التحقق...")
print()

try:
    response = requests.get(IMAGE_URL, timeout=10)
    
    print("=" * 80)
    print("📊 النتيجة:")
    print("=" * 80)
    print()
    print(f"   كود الحالة: {response.status_code}")
    print(f"   نوع المحتوى: {response.headers.get('Content-Type', 'N/A')}")
    print(f"   حجم الملف: {len(response.content)} بايت")
    print()
    
    if response.status_code == 200:
        print("✅ الصورة متاحة!")
        print()
        print("💡 إذا كانت الصورة متاحة لكن القالب لا يزال فاشلاً:")
        print("   1. قد تكون الصورة كبيرة جداً")
        print("   2. قد يكون نوع الصورة غير مدعوم")
        print("   3. قد تكون WhatsApp لا تستطيع الوصول للرابط")
        print()
        
        # حفظ الصورة محلياً للفحص
        with open("downloaded_image.png", "wb") as f:
            f.write(response.content)
        print("💾 تم حفظ الصورة محلياً في: downloaded_image.png")
        print("   افتحها للتأكد من صحتها")
        
    elif response.status_code == 404:
        print("❌ الصورة غير موجودة (404)")
        print()
        print("💡 الحلول:")
        print("   1. تأكد من تشغيل خادم Render")
        print("   2. تحقق من وجود الصورة في مسار /media/job_fair_image.png")
        print("   3. استخدم رابط صورة بديل (Imgur, Cloudinary)")
        
    elif response.status_code == 503:
        print("⚠️ الخادم غير متاح حالياً (503)")
        print()
        print("💡 الحلول:")
        print("   1. انتظر دقائق - قد يكون Render يعيد التشغيل")
        print("   2. تحقق من Render Dashboard")
        print("   3. استخدم رابط صورة بديل مؤقتاً")
        
    else:
        print(f"⚠️ خطأ غير متوقع: {response.status_code}")
    
    print()
    print("=" * 80)
    
except requests.exceptions.Timeout:
    print("❌ انتهت مهلة الطلب (Timeout)")
    print()
    print("💡 الخادم بطيء جداً أو معطل")
    print("   استخدم رابط صورة أسرع")
    
except requests.exceptions.ConnectionError:
    print("❌ فشل الاتصال")
    print()
    print("💡 الحلول:")
    print("   1. تحقق من اتصال الإنترنت")
    print("   2. تأكد من أن خادم Render يعمل")
    print("   3. استخدم رابط صورة بديل")
    
except Exception as e:
    print(f"❌ خطأ: {e}")

print()
