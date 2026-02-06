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
import requests as http_requests
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
CONFIG_FILE = "config.json"

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


def save_invitees(invitees):
    with open(INVITEES_FILE, "w", encoding="utf-8") as f:
        json.dump(invitees, f, ensure_ascii=False, indent=2)


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
# إرسال الدعوات من لوحة التحكم
# ============================================================

def format_saudi_phone(phone):
    """تنسيق رقم الهاتف السعودي"""
    phone = "".join(c for c in str(phone) if c.isdigit())
    if not phone:
        return None
    if phone.startswith("05") and len(phone) == 10:
        phone = "966" + phone[1:]
    elif phone.startswith("5") and len(phone) == 9:
        phone = "966" + phone
    elif phone.startswith("00966"):
        phone = phone[2:]
    elif phone.startswith("966") and len(phone) == 12:
        pass
    if len(phone) != 12 or not phone.startswith("966"):
        return None
    return phone


def get_or_create_template():
    """جلب أو إنشاء قالب الدعوة التفاعلي"""
    # التحقق من وجود قالب محفوظ
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        if config.get("content_sid"):
            return config["content_sid"]

    # إنشاء قالب جديد
    body_text = (
        '🎓 *دعوة رسمية*\n\n'
        'المكرم *{{1}}* حفظه الله\n'
        'السلام عليكم ورحمة الله وبركاته\n\n'
        'يسرّنا دعوتكم لحضور *' + EVENT_NAME + '*\n\n'
        '📅 التاريخ: ' + EVENT_DATE + '\n'
        '🕐 الوقت: ' + EVENT_TIME + '\n'
        '📍 المكان: ' + EVENT_LOCATION + '\n\n'
        'حضوركم يُسعدنا ويُشرّفنا 🌹\n\n'
        '_الكلية التقنية بالأحساء_\n'
        '_المؤسسة العامة للتدريب التقني والمهني_'
    )

    template_data = {
        "friendly_name": "dashboard_invite_" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "language": "ar",
        "variables": {"1": "اسم المدعو"},
        "types": {
            "twilio/quick-reply": {
                "body": body_text,
                "actions": [
                    {"title": "✅ تأكيد الحضور", "id": "accept"},
                    {"title": "❌ اعتذار", "id": "decline"}
                ]
            },
            "twilio/text": {
                "body": body_text + "\n\nللرد: اكتب تأكيد أو اعتذار"
            }
        }
    }

    try:
        resp = http_requests.post(
            "https://content.twilio.com/v1/Content",
            data=json.dumps(template_data),
            headers={"Content-Type": "application/json"},
            auth=(ACCOUNT_SID, AUTH_TOKEN)
        )
        if resp.status_code == 201:
            sid = resp.json().get("sid")
            config = {"content_sid": sid}
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return sid
    except Exception:
        pass
    return None


def send_single_invitation(to_phone, name, content_sid=None):
    """إرسال دعوة واحدة"""
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    # محاولة بالأزرار
    if content_sid:
        try:
            msg = client.messages.create(
                content_sid=content_sid,
                content_variables=json.dumps({"1": name}),
                from_=FROM_PHONE,
                to=f"whatsapp:+{to_phone}"
            )
            return True, msg.sid, "buttons"
        except Exception:
            pass

    # بديل نصي
    body = (
        f"🎓 *دعوة رسمية*\n\n"
        f"المكرم *{name}* حفظه الله\n"
        f"السلام عليكم ورحمة الله وبركاته\n\n"
        f"يسرّنا دعوتكم لحضور *{EVENT_NAME}*\n\n"
        f"📅 التاريخ: {EVENT_DATE}\n"
        f"🕐 الوقت: {EVENT_TIME}\n"
        f"📍 المكان: {EVENT_LOCATION}\n\n"
        f"حضوركم يُسعدنا ويُشرّفنا 🌹\n\n"
        f"─────────────────\n"
        f"📩 *للرد على الدعوة:*\n"
        f"اكتب *تأكيد* أو *1* ← للحضور ✅\n"
        f"اكتب *اعتذار* أو *2* ← للاعتذار ❌"
    )

    try:
        msg = client.messages.create(body=body, from_=FROM_PHONE, to=f"whatsapp:+{to_phone}")
        return True, msg.sid, "text"
    except Exception as e:
        return False, str(e), "error"


@app.route("/api/send", methods=["POST"])
def api_send_invitation():
    """إرسال دعوة من لوحة التحكم"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "بيانات غير صالحة"}), 400

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()

    if not name or not phone:
        return jsonify({"success": False, "error": "الاسم والرقم مطلوبان"}), 400

    formatted = format_saudi_phone(phone)
    if not formatted:
        return jsonify({"success": False, "error": "رقم الهاتف غير صحيح"}), 400

    # حفظ المدعو
    invitees = load_invitees()
    if not any(inv.get("phone") == formatted for inv in invitees):
        invitees.append({
            "name": name, "phone": formatted,
            "department": data.get("department", ""),
            "invited_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_invitees(invitees)

    # إرسال الدعوة
    content_sid = get_or_create_template()
    success, result, msg_type = send_single_invitation(formatted, name, content_sid)

    if success:
        logger.info(f"📨 تم إرسال دعوة إلى {name} ({formatted}) من لوحة التحكم")
        return jsonify({"success": True, "sid": result, "type": msg_type})
    else:
        return jsonify({"success": False, "error": result}), 500


@app.route("/api/send-bulk", methods=["POST"])
def api_send_bulk():
    """إرسال جماعي من لوحة التحكم"""
    data = request.get_json()
    recipients = data.get("recipients", [])

    if not recipients:
        return jsonify({"success": False, "error": "لا يوجد مستلمون"}), 400

    content_sid = get_or_create_template()
    results = []
    invitees = load_invitees()
    existing_phones = {inv.get("phone") for inv in invitees}

    for r in recipients:
        name = r.get("name", "").strip()
        phone = format_saudi_phone(r.get("phone", ""))
        if not name or not phone:
            results.append({"name": name, "status": "خطأ", "error": "بيانات غير صالحة"})
            continue

        if phone not in existing_phones:
            invitees.append({
                "name": name, "phone": phone,
                "department": r.get("department", ""),
                "invited_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            existing_phones.add(phone)

        success, result, msg_type = send_single_invitation(phone, name, content_sid)
        if success:
            results.append({"name": name, "phone": phone, "status": "نجاح", "type": msg_type})
        else:
            results.append({"name": name, "phone": phone, "status": "فشل", "error": result})

        time.sleep(1)  # تأخير بين الرسائل

    save_invitees(invitees)
    success_count = len([r for r in results if r["status"] == "نجاح"])
    logger.info(f"📤 إرسال جماعي: {success_count}/{len(results)} نجاح")

    return jsonify({"success": True, "results": results, "sent": success_count, "total": len(results)})


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
