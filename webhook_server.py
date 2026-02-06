"""
خادم الويب هوك - نظام دعوات واتساب التفاعلي
WhatsApp Invitation Webhook Server

يستقبل ردود المدعوين عبر واتساب ويرد تلقائياً
يوفر API للوحة المتابعة (Dashboard)
يشغل ngrok تلقائياً لإنشاء رابط عام

الاستخدام:
    python webhook_server.py
"""

import os
import sys
import json
import csv
import logging
import threading
import time
from datetime import datetime
from io import StringIO

# تحميل المتغيرات من ملف .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# إصلاح ترميز الطرفية في Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from flask import Flask, request, jsonify, send_file, Response
except ImportError:
    print("=" * 50)
    print("خطأ: مكتبة Flask غير مثبّتة")
    print("قم بتشغيل: pip install flask")
    print("=" * 50)
    sys.exit(1)

try:
    from twilio.rest import Client
    from twilio.twiml.messaging_response import MessagingResponse
except ImportError:
    print("=" * 50)
    print("خطأ: مكتبة Twilio غير مثبّتة")
    print("قم بتشغيل: pip install twilio")
    print("=" * 50)
    sys.exit(1)

# ============================================================
# الإعدادات
# ============================================================

ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
FROM_PHONE = os.environ.get("TWILIO_FROM_PHONE", "whatsapp:+14155238886")

EVENT_NAME = "حفل تخريج الدفعة ٢٠٢٦"
EVENT_DATE = "الأحد ١٥ شعبان ١٤٤٧هـ"
EVENT_TIME = "٧:٠٠ مساءً"
EVENT_LOCATION = "قاعة الاحتفالات الرئيسية - الكلية التقنية بالأحساء"

INVITEES_FILE = "invitees.json"
RESPONSES_FILE = "responses.json"

# ============================================================
# إعداد التسجيل
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("webhook_log.txt", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# Flask Application
# ============================================================

app = Flask(__name__)

# ============================================================
# دوال البيانات
# ============================================================

def load_invitees():
    if os.path.exists(INVITEES_FILE):
        with open(INVITEES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def load_responses():
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_responses(responses):
    with open(RESPONSES_FILE, "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)


def find_invitee_by_phone(phone):
    """البحث عن المدعو بالرقم"""
    phone_clean = phone.replace("whatsapp:", "").replace("+", "").strip()
    # آخر 9 أرقام للمقارنة
    phone_suffix = phone_clean[-9:] if len(phone_clean) >= 9 else phone_clean

    invitees = load_invitees()
    for inv in invitees:
        inv_suffix = inv.get("phone", "")[-9:]
        if inv_suffix == phone_suffix:
            return inv

    return None


# ============================================================
# كلمات القبول والاعتذار
# ============================================================

ACCEPT_KEYWORDS = [
    "accept", "تأكيد", "تاكيد", "نعم", "حاضر", "أحضر", "احضر",
    "سأحضر", "ساحضر", "موافق", "قبول", "1",
    "✅ تأكيد الحضور", "تأكيد الحضور", "تاكيد الحضور"
]

DECLINE_KEYWORDS = [
    "decline", "اعتذار", "إعتذار", "لا", "أعتذر", "اعتذر",
    "معتذر", "لن أحضر", "لن احضر", "رفض", "2",
    "❌ اعتذار", "❌ إعتذار"
]


def classify_response(text):
    """تصنيف رد المدعو"""
    text = text.strip().lower()
    # إزالة الإيموجي للمقارنة
    clean = text.replace("✅", "").replace("❌", "").strip()

    for keyword in ACCEPT_KEYWORDS:
        if text == keyword.lower() or clean == keyword.lower():
            return "accept"

    for keyword in DECLINE_KEYWORDS:
        if text == keyword.lower() or clean == keyword.lower():
            return "decline"

    return "unknown"


# ============================================================
# Webhook Endpoint - يستقبل رسائل واتساب من Twilio
# ============================================================

@app.route("/webhook", methods=["POST"])
def webhook():
    """استقبال ردود واتساب من Twilio والرد التلقائي"""

    # بيانات الرسالة الواردة
    from_number = request.form.get("From", "")
    body = request.form.get("Body", "").strip()
    button_payload = request.form.get("ButtonPayload", "").strip()

    logger.info(f"📨 رسالة واردة من {from_number}: '{body}' (payload: '{button_payload}')")

    # تحديد نوع الرد (من الزر أو من النص)
    action_text = button_payload if button_payload else body
    action = classify_response(action_text)

    # البحث عن المدعو
    invitee = find_invitee_by_phone(from_number)
    phone_clean = from_number.replace("whatsapp:", "").replace("+", "")
    name = invitee["name"] if invitee else phone_clean

    # إنشاء الرد التلقائي
    resp = MessagingResponse()

    if action == "accept":
        status = "تأكيد حضور"
        reply = (
            f"✅ *تم تأكيد حضورك بنجاح!*\n"
            f"\n"
            f"أهلاً *{name}* 🎉\n"
            f"\n"
            f"نتشرف بحضورك في *{EVENT_NAME}*\n"
            f"\n"
            f"📅 {EVENT_DATE}\n"
            f"🕐 {EVENT_TIME}\n"
            f"📍 {EVENT_LOCATION}\n"
            f"\n"
            f"في انتظار حضورك! 🌹\n"
            f"\n"
            f"_الكلية التقنية بالأحساء_"
        )
        logger.info(f"✅ {name} أكّد الحضور")

    elif action == "decline":
        status = "اعتذار"
        reply = (
            f"تم تسجيل اعتذارك *{name}*\n"
            f"\n"
            f"نشكرك على الرد 🙏\n"
            f"نتمنى لك التوفيق دائماً\n"
            f"وستبقى مدعواً في مناسباتنا القادمة 💚\n"
            f"\n"
            f"_الكلية التقنية بالأحساء_"
        )
        logger.info(f"❌ {name} اعتذر عن الحضور")

    else:
        status = None
        reply = (
            f"مرحباً! 👋\n"
            f"\n"
            f"للرد على دعوة *{EVENT_NAME}*:\n"
            f"\n"
            f"✅ اكتب *تأكيد* أو *1* للحضور\n"
            f"❌ اكتب *اعتذار* أو *2* للاعتذار\n"
            f"\n"
            f"_الكلية التقنية بالأحساء_"
        )
        logger.info(f"❓ رسالة غير مفهومة من {name}: '{body}'")

    resp.message(reply)

    # حفظ الرد في قاعدة البيانات
    if status:
        responses = load_responses()

        # التحقق من وجود رد سابق (تحديث بدلاً من إضافة)
        existing = None
        for r in responses:
            if r.get("phone") == phone_clean:
                existing = r
                break

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if existing:
            existing["status"] = status
            existing["timestamp"] = now
            existing["name"] = name  # تحديث الاسم في حال تغير
            logger.info(f"  🔄 تم تحديث رد {name}")
        else:
            responses.append({
                "id": int(datetime.now().timestamp() * 1000),
                "name": name,
                "phone": phone_clean,
                "status": status,
                "timestamp": now
            })
            logger.info(f"  💾 تم حفظ رد جديد من {name}")

        save_responses(responses)

    return str(resp), 200, {"Content-Type": "text/xml"}


# ============================================================
# API Endpoints - للوحة المتابعة
# ============================================================

@app.route("/api/responses", methods=["GET"])
def api_get_responses():
    """جلب جميع الردود"""
    responses = load_responses()
    return jsonify(responses)


@app.route("/api/invitees", methods=["GET"])
def api_get_invitees():
    """جلب جميع المدعوين"""
    invitees = load_invitees()
    return jsonify(invitees)


@app.route("/api/stats", methods=["GET"])
def api_get_stats():
    """جلب الإحصائيات"""
    responses = load_responses()
    invitees = load_invitees()

    total_invited = len(invitees)
    total_responded = len(responses)
    accepted = len([r for r in responses if r.get("status") == "تأكيد حضور"])
    declined = len([r for r in responses if r.get("status") == "اعتذار"])
    pending = total_invited - total_responded

    return jsonify({
        "total_invited": total_invited,
        "total_responded": total_responded,
        "accepted": accepted,
        "declined": declined,
        "pending": max(0, pending)
    })


@app.route("/api/responses/<int:response_id>", methods=["DELETE"])
def api_delete_response(response_id):
    """حذف رد واحد"""
    responses = load_responses()
    responses = [r for r in responses if r.get("id") != response_id]
    save_responses(responses)
    return jsonify({"success": True})


@app.route("/api/responses/clear", methods=["DELETE"])
def api_clear_responses():
    """مسح جميع الردود"""
    save_responses([])
    return jsonify({"success": True})


@app.route("/api/export", methods=["GET"])
def api_export_csv():
    """تصدير الردود كملف CSV"""
    responses = load_responses()

    if not responses:
        return jsonify({"error": "لا توجد بيانات"}), 404

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["الاسم", "رقم الهاتف", "الحالة", "وقت الرد"])

    for r in responses:
        writer.writerow([
            r.get("name", ""),
            r.get("phone", ""),
            r.get("status", ""),
            r.get("timestamp", "")
        ])

    csv_content = "\ufeff" + output.getvalue()
    return Response(
        csv_content,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=responses_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


# ============================================================
# صفحات الويب
# ============================================================

@app.route("/")
@app.route("/dashboard")
def serve_dashboard():
    """عرض لوحة المتابعة"""
    return send_file("dashboard.html")


@app.route("/invitation")
def serve_invitation():
    """عرض صفحة الدعوة"""
    if os.path.exists("whatsapp_invitation.html"):
        return send_file("whatsapp_invitation.html")
    return "File not found", 404


# ============================================================
# تشغيل ngrok تلقائياً
# ============================================================

def start_ngrok(port=5000):
    """تشغيل ngrok وإرجاع الرابط العام"""
    try:
        from pyngrok import ngrok, conf

        # إعداد pyngrok
        conf.get_default().region = "us"

        # فتح نفق ngrok
        public_url = ngrok.connect(port, "http").public_url

        # تحويل http إلى https
        if public_url.startswith("http://"):
            public_url = public_url.replace("http://", "https://")

        return public_url

    except ImportError:
        logger.warning("مكتبة pyngrok غير مثبتة: pip install pyngrok")
        return None
    except Exception as e:
        logger.warning(f"فشل تشغيل ngrok: {e}")
        return None


def configure_twilio_webhook(webhook_url):
    """محاولة تحديث Webhook URL في Twilio تلقائياً (Sandbox)"""
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        # تحديث sandbox webhook عبر API (إذا كان ممكناً)
        logger.info(f"  📋 يرجى تحديث Webhook URL يدوياً في Twilio Sandbox")
    except Exception:
        pass


# ============================================================
# التشغيل
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    is_cloud = os.environ.get("RENDER") or os.environ.get("PORT")

    print()
    print("=" * 60)
    print("  خادم الويب هوك - نظام دعوات واتساب التفاعلي")
    print("  الكلية التقنية بالأحساء")
    print("=" * 60)

    if is_cloud:
        # تشغيل على Render.com أو سيرفر سحابي
        print()
        print(f"  تشغيل سحابي على المنفذ {port}")
        print(f"  الويب هوك جاهز على /webhook")
        print()
    else:
        # تشغيل محلي - محاولة تشغيل ngrok
        print()
        print("  جاري تشغيل ngrok...")
        ngrok_url = start_ngrok(port)

        if ngrok_url:
            webhook_url = f"{ngrok_url}/webhook"
            print()
            print(f"  ngrok يعمل بنجاح!")
            print(f"  الرابط العام:    {ngrok_url}")
            print(f"  رابط الويب هوك:  {webhook_url}")
            print()
            print("  ─────────────────────────────────────────────────")
            print("  افتح Twilio Sandbox:")
            print("  https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
            print()
            print(f"  في حقل 'WHEN A MESSAGE COMES IN' ضع:")
            print(f"  {webhook_url}")
            print("  ─────────────────────────────────────────────────")
        else:
            print()
            print("  لم نتمكن من تشغيل ngrok تلقائيا")

        print()
        print(f"  لوحة المتابعة:  http://localhost:{port}/dashboard")
        print()

    app.run(host="0.0.0.0", port=port, debug=False)
