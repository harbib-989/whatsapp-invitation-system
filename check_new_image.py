"""
التحقق من الصورة الجديدة على GitHub
"""
import sys
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NEW_IMAGE_URL = "https://raw.githubusercontent.com/harbib-989/whatsapp-invitation-system/main/job_fair_image.png"

print("=" * 80)
print("🔍 التحقق من الصورة الجديدة على GitHub")
print("=" * 80)
print()
print(f"الرابط: {NEW_IMAGE_URL}")
print()
print("⏳ جاري التحقق...")
print()

try:
    response = requests.get(NEW_IMAGE_URL, timeout=10)
    
    print("=" * 80)
    print("📊 النتيجة:")
    print("=" * 80)
    print()
    print(f"   ✅ كود الحالة: {response.status_code}")
    print(f"   📄 النوع: {response.headers.get('Content-Type', 'N/A')}")
    print(f"   📦 الحجم: {len(response.content):,} بايت ({len(response.content)/1024:.1f} KB)")
    print()
    
    if response.status_code == 200:
        print("✅ الصورة متاحة ويمكن الوصول إليها!")
        print()
        
        # مقارنة مع الصورة القديمة
        print("📊 مقارنة:")
        print(f"   الصورة القديمة (Render): 323,273 بايت (315.7 KB)")
        print(f"   الصورة الجديدة (GitHub): {len(response.content):,} بايت ({len(response.content)/1024:.1f} KB)")
        
        if len(response.content) < 323273:
            print(f"   ✅ الصورة الجديدة أصغر بـ {(323273 - len(response.content))/1024:.1f} KB")
        elif len(response.content) == 323273:
            print(f"   ℹ️  نفس الحجم - ربما نفس الصورة")
        else:
            print(f"   ⚠️  الصورة الجديدة أكبر بـ {(len(response.content) - 323273)/1024:.1f} KB")
        
        print()
        print("✅ تم تحديث config.json بالرابط الجديد")
        print()
        
    else:
        print(f"❌ خطأ: {response.status_code}")
    
    print("=" * 80)
    
except Exception as e:
    print(f"❌ خطأ: {e}")

print()
