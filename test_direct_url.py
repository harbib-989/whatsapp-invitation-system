import requests
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

url = "https://raw.githubusercontent.com/harbib-989/whatsapp-invitation-system/main/job_fair_image.png"

print("جاري اختبار الرابط المباشر...")
print()

try:
    r = requests.get(url, timeout=10)
    print(f"كود الحالة: {r.status_code}")
    print(f"الحجم: {len(r.content):,} بايت ({len(r.content)/1024:.1f} KB)")
    print(f"النوع: {r.headers.get('Content-Type')}")
    print()
    if r.status_code == 200:
        print("✅ الرابط المباشر يعمل!")
    else:
        print("❌ الرابط لا يعمل")
except Exception as e:
    print(f"❌ خطأ: {e}")
