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
FROM_PHONE = os.environ.get("TWILIO_FROM_PHONE", "whatsapp:+966550308539")

# قوالب المحتوى
DIALOGUE_CONTENT_SID = "HX5f92c7470551312f6d1d461f16dafdb6"  # حوار: دور الرؤية
JOB_FAIR_CONTENT_SID = "HX7f91572f7f87564aa0265dbe20b6ae12"   # ملتقى الكفاءات - دعوة عامة
# القالب الرسمي للمسؤولين يُنشأ عبر create_vip_template.py ثم يُضاف هنا أو في env

def get_available_templates():
    """القوالب المتاحة للاختيار عند الإرسال"""
    cfg = _load_config()
    vip_sid = os.environ.get("CONTENT_SID_VIP") or cfg.get("content_sid_vip", "")

    templates = [
        {
            "id": "standard",
            "name": "دعوة عامة - ملتقى الكفاءات",
            "content_sid": JOB_FAIR_CONTENT_SID,
            "variables": 1,
            "position_required": False,
        },
    ]
    if vip_sid:
        templates.append({
            "id": "vip",
            "name": "دعوة رسمية - للمسؤولين وكبار الشخصيات",
            "content_sid": vip_sid,
            "variables": 2,
            "position_required": True,
        })
    return templates

INVITEES_FILE = "invitees.json"
RESPONSES_FILE = "responses.json"
CONFIG_FILE = "config.json"

# تحميل الإعدادات: أولاً من env (لـ Render)، ثم config.json، ثم القيم الافتراضية
def _load_config():
    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    return cfg

_config_cache = {}

def get_event_config():
    """تفاصيل الفعالية الحالية - للرد التلقائي والإرسال"""
    if _config_cache:
        return _config_cache

    cfg = _load_config()
    mode = os.environ.get("EVENT_MODE", cfg.get("event_mode", "dialogue"))

    if mode == "job_fair":
        _config_cache.update({
            "event_name": "ملتقى الكفاءات التقنية",
            "event_date": "يوم الأحد 15",
            "event_time": "لمدة يومين",
            "event_location": "مسرح الكلية التقنية - الكلية التقنية بالأحساء",
            "accept_tips": (
                "💡 نصائح مهمة:\n"
                "• أحضر سيرتك الذاتية مطبوعة\n"
                "• ارتدِ ملابس رسمية\n"
                "• كن مستعداً للمقابلات الفورية\n"
            ),
            "content_sid": os.environ.get("CONTENT_SID") or cfg.get("content_sid") or JOB_FAIR_CONTENT_SID,
        })
    else:
        # افتراضي: حوار دور الرؤية
        _config_cache.update({
            "event_name": "حوار: دور الرؤية في تعزيز الهوية الوطنية",
            "event_date": "الإثنين ٢١ شعبان ١٤٤٧هـ",
            "event_time": "١٠:٠٠ صباحاً",
            "event_location": "مسرح الكلية مبنى ٩ - الكلية التقنية بالأحساء",
            "accept_tips": "",
            "content_sid": os.environ.get("CONTENT_SID") or cfg.get("content_sid") or DIALOGUE_CONTENT_SID,
        })
    return _config_cache

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

app = Flask(__name__, static_folder="static", static_url_path="/static")

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
    """تصنيف رد المدعو - يدعم النصوص والأزرار"""
    text = text.strip().lower()
    
    # دعم Button IDs من Quick Reply
    if text in ["confirm_attendance", "confirm", "accept_button"]:
        return "accept"
    if text in ["decline_attendance", "decline", "decline_button"]:
        return "decline"
    
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

    # البحث عن المدعو - إن لم يُعثر عليه استخدم "عزيزي المدعو" بدل الرقم
    invitee = find_invitee_by_phone(from_number)
    phone_clean = from_number.replace("whatsapp:", "").replace("+", "")
    name = invitee["name"] if invitee else "عزيزي المدعو"

    ev = get_event_config()

    # إنشاء الرد التلقائي
    resp = MessagingResponse()

    if action == "accept":
        status = "تأكيد حضور"
        tips = ev.get("accept_tips", "")
        tips_block = f"\n{tips}\n" if tips else "\n"
        reply = (
            f"✅ *تم تأكيد حضورك بنجاح!*\n"
            f"\n"
            f"شكراً *{name}* 🎉\n"
            f"\n"
            f"نتشرف بحضورك في:\n"
            f"💼 *{ev['event_name']}*\n"
            f"\n"
            f"📅 {ev['event_date']} - {ev['event_time']}\n"
            f"📍 {ev['event_location']}\n"
            f"{tips_block}"
            f"سنرسل لك تذكيراً قبل الفعالية 📲\n"
            f"\n"
            f"في انتظار حضورك! 🌟\n"
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
            f"نتمنى لك التوفيق دائماً ونأمل رؤيتك في الفعاليات القادمة 💚\n"
            f"\n"
            f"_الكلية التقنية بالأحساء_"
        )
        logger.info(f"❌ {name} اعتذر عن الحضور")

    else:
        status = None
        reply = (
            f"مرحباً *{name}*! 👋\n"
            f"\n"
            f"للرد على دعوة *{ev['event_name']}*:\n"
            f"\n"
            f"✅ اكتب: *تأكيد* أو *1* للحضور\n"
            f"❌ اكتب: *اعتذار* أو *2* للاعتذار\n"
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

@app.route("/api/templates", methods=["GET"])
def api_get_templates():
    """جلب القوالب المتاحة للإرسال"""
    return jsonify(get_available_templates())


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
    ev = get_event_config()
    content_sid = ev.get("content_sid")

    # التحقق من وجود قالب محفوظ في config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            if config.get("content_sid"):
                return config["content_sid"]
        except Exception:
            pass

    if content_sid:
        return content_sid

    # إنشاء قالب جديد (بدون إيموجي في الأزرار - شرط WhatsApp Business API)
    body_text = (
        'دعوة رسمية\n\n'
        'المكرم {{1}} حفظه الله\n'
        'السلام عليكم ورحمة الله وبركاته\n\n'
        'يسرنا دعوتكم لحضور ' + ev["event_name"] + '\n\n'
        'التاريخ: ' + ev["event_date"] + '\n'
        'الوقت: ' + ev["event_time"] + '\n'
        'المكان: ' + ev["event_location"] + '\n\n'
        'حضوركم يسعدنا ويشرفنا\n\n'
        'الكلية التقنية بالاحساء\n'
        'المؤسسة العامة للتدريب التقني والمهني'
    )

    template_data = {
        "friendly_name": "invite_" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "language": "ar",
        "variables": {"1": "Guest"},
        "types": {
            "twilio/quick-reply": {
                "body": body_text,
                "actions": [
                    {"title": "تاكيد الحضور", "id": "accept"},
                    {"title": "اعتذار", "id": "decline"}
                ]
            },
            "twilio/text": {
                "body": body_text + "\n\nللرد اكتب تاكيد او اعتذار"
            }
        }
    }

    try:
        resp = http_requests.post(
            "https://content.twilio.com/v1/Content",
            json=template_data,
            auth=(ACCOUNT_SID, AUTH_TOKEN)
        )
        if resp.status_code == 201:
            sid = resp.json().get("sid")
            # طلب الاعتماد من WhatsApp
            http_requests.post(
                f"https://content.twilio.com/v1/Content/{sid}/ApprovalRequests/whatsapp",
                json={"name": "invite_" + datetime.now().strftime("%Y%m%d%H%M%S"), "category": "UTILITY"},
                auth=(ACCOUNT_SID, AUTH_TOKEN)
            )
            config = {"content_sid": sid}
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return sid
    except Exception:
        pass
    return None


def get_image_url():
    """جلب رابط صورة الدعوة من ملف الإعدادات"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("image_url", "")
        except Exception:
            pass
    return ""


def get_base_url():
    """جلب رابط السيرفر الأساسي"""
    # على Render
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if render_url:
        return render_url
    return "https://whatsapp-invitation-system.onrender.com"


def send_single_invitation(to_phone, name, content_sid=None, template_id=None, position=""):
    """إرسال دعوة واحدة مع أزرار تفاعلية
    template_id: standard | vip - إن لم يُحدد يُستخدم content_sid أو الافتراضي
    position: المنصب (مطلوب للقالب الرسمي)
    """
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    ev = get_event_config()

    # تحديد القالب
    if template_id:
        for t in get_available_templates():
            if t["id"] == template_id:
                content_sid = t["content_sid"]
                is_vip = t.get("variables", 1) == 2
                break
        else:
            content_sid = get_or_create_template() or ev["content_sid"]
            is_vip = False
    elif not content_sid:
        content_sid = get_or_create_template() or ev["content_sid"]
        is_vip = False
    else:
        is_vip = any(t.get("variables") == 2 and t["content_sid"] == content_sid for t in get_available_templates())

    # متغيرات القالب: القالب الرسمي يستخدم الاسم + المنصب (مثل: مدير الإدارة، رئيس القسم)
    if is_vip:
        content_vars = {"1": name, "2": position.strip() if position else "الكرام"}
    else:
        content_vars = {"1": name}

    # محاولة 1: إرسال WhatsApp Card بأزرار (إذا معتمد من WhatsApp)
    try:
        msg = client.messages.create(
            content_sid=content_sid,
            content_variables=json.dumps(content_vars),
            from_=FROM_PHONE,
            to=f"whatsapp:+{to_phone}"
        )
        logger.info(f"✅ تم إرسال دعوة بأزرار WhatsApp Card إلى {name}")
        return True, msg.sid, "whatsapp_card"
    except Exception as e:
        logger.warning(f"⚠️ فشل إرسال WhatsApp Card (قد يكون غير معتمد بعد): {e}")
    
    # محاولة 2: Fallback - إرسال رسالة نصية
    image_url = get_image_url() or (
        "https://raw.githubusercontent.com/harbib-989/whatsapp-invitation-system/main/job_fair_image.png"
        if ev.get("event_name", "").find("ملتقى") >= 0 else ""
    )

    if is_vip:
        greeting = f"المكرم *{name}* {position.strip() if position else 'الكرام'} حفظه الله"
    else:
        greeting = f"عزيزي *{name}*"

    body = (
        f"💼 *دعوة رسمية*\n\n"
        f"{greeting}\n"
        f"السلام عليكم ورحمة الله وبركاته 🌹\n\n"
        f"يسرنا دعوتكم لحضور:\n\n"
        f"*{ev['event_name']}*\n\n"
        f"📅 التاريخ: {ev['event_date']}\n"
        f"🕐 الوقت: {ev['event_time']}\n"
        f"📍 المكان: {ev['event_location']}\n\n"
        f"حضوركم يُسعدنا ويُشرّفنا 🌹\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔹 للرد على الدعوة:\n"
        f"✅ اكتب: *تأكيد* أو *1* للحضور\n"
        f"❌ اكتب: *اعتذار* أو *2* للاعتذار\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"_الكلية التقنية بالأحساء_"
    )

    try:
        msg_params = {
            "body": body,
            "from_": FROM_PHONE,
            "to": f"whatsapp:+{to_phone}"
        }
        
        # إرسال الصورة مع الرسالة
        if image_url:
            msg_params["media_url"] = [image_url]

        msg = client.messages.create(**msg_params)
        logger.info(f"✅ تم إرسال دعوة نصية مع صورة إلى {name}")
        return True, msg.sid, "text_with_image"
    except Exception as e:
        logger.error(f"❌ فشل إرسال الدعوة إلى {name}: {e}")
        return False, str(e), "error"


@app.route("/api/send", methods=["POST"])
def api_send_invitation():
    """إرسال دعوة من لوحة التحكم"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "بيانات غير صالحة"}), 400

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    template_id = data.get("template_id", "standard")
    position = data.get("position", "").strip()

    if not name or not phone:
        return jsonify({"success": False, "error": "الاسم والرقم مطلوبان"}), 400

    # التحقق: القالب الرسمي يتطلب المنصب
    for t in get_available_templates():
        if t["id"] == template_id and t.get("position_required") and not position:
            return jsonify({"success": False, "error": "المنصب مطلوب للدعوة الرسمية"}), 400

    formatted = format_saudi_phone(phone)
    if not formatted:
        return jsonify({"success": False, "error": "رقم الهاتف غير صحيح"}), 400

    # حفظ المدعو
    invitees = load_invitees()
    if not any(inv.get("phone") == formatted for inv in invitees):
        invitees.append({
            "name": name, "phone": formatted,
            "department": data.get("department", ""),
            "position": position,
            "invited_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_invitees(invitees)

    # إرسال الدعوة
    success, result, msg_type = send_single_invitation(
        formatted, name, template_id=template_id, position=position
    )

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
    template_id = data.get("template_id", "standard")

    if not recipients:
        return jsonify({"success": False, "error": "لا يوجد مستلمون"}), 400

    results = []
    invitees = load_invitees()
    existing_phones = {inv.get("phone") for inv in invitees}

    for r in recipients:
        name = r.get("name", "").strip()
        phone = format_saudi_phone(r.get("phone", ""))
        position = r.get("position", "").strip()

        if not name or not phone:
            results.append({"name": name, "status": "خطأ", "error": "بيانات غير صالحة"})
            continue

        # القالب الرسمي يتطلب المنصب
        req_pos = any(t["id"] == template_id and t.get("position_required") for t in get_available_templates())
        if req_pos and not position:
            results.append({"name": name, "status": "خطأ", "error": "المنصب مطلوب"})
            continue

        if phone not in existing_phones:
            invitees.append({
                "name": name, "phone": phone,
                "department": r.get("department", ""),
                "position": position,
                "invited_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            existing_phones.add(phone)

        success, result, msg_type = send_single_invitation(
            phone, name, template_id=template_id, position=position
        )
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


@app.route("/media/invitation.png")
def serve_invitation_image():
    """خدمة صورة الدعوة مع Content-Type صحيح"""
    img_path = os.path.join("static", "invitation.png")
    if os.path.exists(img_path):
        return send_file(img_path, mimetype="image/png")
    return "Image not found", 404


@app.route("/invitation-image")
def serve_invitation_image_alt():
    """تقديم صورة الدعوة (رابط بديل)"""
    img_path = os.path.join("static", "invitation.png")
    if os.path.exists(img_path):
        return send_file(img_path, mimetype="image/png")
    return "Image not found", 404


@app.route("/decline_form.html")
def serve_decline_form():
    """عرض صفحة الاعتذار"""
    if os.path.exists("decline_form.html"):
        return send_file("decline_form.html")
    return "File not found", 404


@app.route("/job_fair_invitation.html")
def serve_job_fair_invitation():
    """عرض صفحة دعوة ملتقى التوظيف"""
    if os.path.exists("job_fair_invitation.html"):
        return send_file("job_fair_invitation.html")
    return "File not found", 404


@app.route("/webhook/decline", methods=["POST"])
def webhook_decline():
    """معالجة نموذج الاعتذار عن الحضور"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "بيانات غير صالحة"}), 400
        
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        reason = data.get("reason", "").strip()
        details = data.get("details", "").strip()
        future_events = data.get("futureEvents", False)
        
        if not name or not phone:
            return jsonify({"success": False, "error": "الاسم والرقم مطلوبان"}), 400
        
        # تنسيق رقم الهاتف
        formatted_phone = format_saudi_phone(phone)
        if not formatted_phone:
            return jsonify({"success": False, "error": "رقم الهاتف غير صحيح"}), 400
        
        # حفظ الاعتذار
        responses = load_responses()
        
        decline_data = {
            "name": name,
            "phone": formatted_phone,
            "status": "decline",
            "reason": reason,
            "details": details,
            "future_events": future_events,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "web_form"
        }
        
        # تحديث أو إضافة الرد
        existing_idx = next((i for i, r in enumerate(responses) if r.get("phone") == formatted_phone), None)
        if existing_idx is not None:
            responses[existing_idx] = decline_data
        else:
            responses.append(decline_data)
        
        save_responses(responses)
        
        logger.info(f"❌ اعتذار جديد من {name} ({formatted_phone}) - السبب: {reason}")
        
        # إرسال رسالة شكر عبر واتساب (اختياري)
        try:
            if ACCOUNT_SID and AUTH_TOKEN:
                client = Client(ACCOUNT_SID, AUTH_TOKEN)
                ev = get_event_config()
                thank_you_msg = (
                    f"شكراً {name}،\n\n"
                    f"تم استلام اعتذارك عن حضور {ev['event_name']}.\n"
                    f"نتمنى لك كل التوفيق ونأمل رؤيتك في الفعاليات القادمة.\n\n"
                    f"الكلية التقنية بالأحساء"
                )
                client.messages.create(
                    body=thank_you_msg,
                    from_=FROM_PHONE,
                    to=f"whatsapp:+{formatted_phone}"
                )
                logger.info(f"✅ تم إرسال رسالة شكر إلى {name}")
        except Exception as e:
            logger.warning(f"فشل إرسال رسالة الشكر: {e}")
        
        return jsonify({
            "success": True,
            "message": "تم إرسال اعتذارك بنجاح"
        })
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الاعتذار: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


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
