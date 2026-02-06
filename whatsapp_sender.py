"""
نظام إرسال دعوات واتساب التفاعلي
Interactive WhatsApp Invitation System via Twilio

الميزات:
    - إرسال دعوات مع أزرار تفاعلية (تأكيد / اعتذار)
    - إنشاء قوالب المحتوى تلقائياً (Content Templates)
    - دعم الإرسال الفردي والجماعي
    - حفظ قائمة المدعوين للاستخدام مع Webhook

الاستخدام:
    python whatsapp_sender.py
"""

import csv
import os
import sys
import time
import json
import logging
from datetime import datetime

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
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
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

CSV_FILE = "recipients.csv"
CONFIG_FILE = "config.json"
INVITEES_FILE = "invitees.json"

# تفاصيل الفعالية
EVENT_NAME = "حفل تخريج الدفعة ٢٠٢٦"
EVENT_DATE = "الأحد ١٥ شعبان ١٤٤٧هـ"
EVENT_TIME = "٧:٠٠ مساءً"
EVENT_LOCATION = "قاعة الاحتفالات الرئيسية - الكلية التقنية بالأحساء"

DELAY_BETWEEN_MESSAGES = 2

# ============================================================
# إعداد التسجيل
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("send_log.txt", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# ملفات التكوين والبيانات
# ============================================================

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_invitees():
    if os.path.exists(INVITEES_FILE):
        with open(INVITEES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_invitees(invitees):
    with open(INVITEES_FILE, "w", encoding="utf-8") as f:
        json.dump(invitees, f, ensure_ascii=False, indent=2)


# ============================================================
# تنسيق رقم الهاتف السعودي
# ============================================================

def format_saudi_phone(phone):
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


# ============================================================
# إنشاء قالب المحتوى التفاعلي (Content Template)
# ============================================================

def setup_content_template(client):
    """إنشاء قالب دعوة بأزرار تفاعلية (مرة واحدة فقط)"""
    config = load_config()

    # التحقق من وجود قالب سابق
    if config.get("content_sid"):
        try:
            existing = client.content.v1.contents(config["content_sid"]).fetch()
            logger.info(f"  ✅ القالب موجود: {config['content_sid']}")
            return config["content_sid"]
        except Exception:
            logger.info("  القالب السابق غير صالح، سيتم إنشاء قالب جديد...")

    logger.info("  جاري إنشاء قالب الدعوة التفاعلي...")

    body_text = (
        '🎓 *دعوة رسمية*\n'
        '\n'
        'المكرم *{{1}}* حفظه الله\n'
        'السلام عليكم ورحمة الله وبركاته\n'
        '\n'
        'يسرّنا دعوتكم لحضور *' + EVENT_NAME + '*\n'
        '\n'
        '📅 التاريخ: ' + EVENT_DATE + '\n'
        '🕐 الوقت: ' + EVENT_TIME + '\n'
        '📍 المكان: ' + EVENT_LOCATION + '\n'
        '\n'
        'حضوركم يُسعدنا ويُشرّفنا 🌹\n'
        '\n'
        '_الكلية التقنية بالأحساء_\n'
        '_المؤسسة العامة للتدريب التقني والمهني_'
    )

    try:
        import requests as http_requests

        # استخدام Twilio Content API مباشرة (HTTP)
        template_data = {
            "friendly_name": "graduation_invitation_" + datetime.now().strftime("%Y%m%d%H%M%S"),
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

        response = http_requests.post(
            "https://content.twilio.com/v1/Content",
            data=json.dumps(template_data),
            headers={"Content-Type": "application/json"},
            auth=(ACCOUNT_SID, AUTH_TOKEN)
        )

        if response.status_code != 201:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        content_sid = response.json().get("sid")
        config["content_sid"] = content_sid
        save_config(config)
        logger.info(f"  ✅ تم إنشاء القالب: {content_sid}")

        # طلب الموافقة على القالب
        try:
            client.content.v1.contents(content_sid).approval_requests.create()
            logger.info("  📋 تم طلب الموافقة على القالب")
        except Exception:
            pass

        return content_sid

    except Exception as e:
        logger.warning(f"  ⚠️ لم نتمكن من إنشاء قالب بأزرار: {e}")
        logger.info("  سيتم استخدام الرسائل النصية مع تعليمات الرد")
        return None


# ============================================================
# إرسال الدعوة
# ============================================================

def send_invitation(client, to_phone, name, content_sid=None, department=""):
    """إرسال دعوة تفاعلية مع أزرار، أو رسالة نصية كبديل"""

    # المحاولة الأولى: إرسال برسالة تفاعلية بأزرار
    if content_sid:
        try:
            message = client.messages.create(
                content_sid=content_sid,
                content_variables=json.dumps({"1": name}),
                from_=FROM_PHONE,
                to=f"whatsapp:+{to_phone}"
            )
            return True, message.sid, "buttons"
        except Exception as e:
            logger.warning(f"  ⚠️ فشل إرسال الأزرار، محاولة بالنص: {e}")

    # البديل: رسالة نصية مع تعليمات الرد
    dept_line = f"({department}) " if department else ""
    body = (
        f"🎓 *دعوة رسمية*\n"
        f"\n"
        f"المكرم *{name}* {dept_line}حفظه الله\n"
        f"السلام عليكم ورحمة الله وبركاته\n"
        f"\n"
        f"يسرّنا دعوتكم لحضور *{EVENT_NAME}*\n"
        f"\n"
        f"📅 التاريخ: {EVENT_DATE}\n"
        f"🕐 الوقت: {EVENT_TIME}\n"
        f"📍 المكان: {EVENT_LOCATION}\n"
        f"\n"
        f"حضوركم يُسعدنا ويُشرّفنا 🌹\n"
        f"\n"
        f"─────────────────\n"
        f"📩 *للرد على الدعوة:*\n"
        f"اكتب *تأكيد* أو *1* ← للحضور ✅\n"
        f"اكتب *اعتذار* أو *2* ← للاعتذار ❌\n"
        f"\n"
        f"_الكلية التقنية بالأحساء_"
    )

    try:
        message = client.messages.create(
            body=body,
            from_=FROM_PHONE,
            to=f"whatsapp:+{to_phone}"
        )
        return True, message.sid, "text"
    except TwilioRestException as e:
        return False, str(e), "error"
    except Exception as e:
        return False, str(e), "error"


# ============================================================
# قراءة المستلمين
# ============================================================

def load_recipients_csv(csv_path):
    recipients = []
    if not os.path.exists(csv_path):
        logger.error(f"ملف CSV غير موجود: {csv_path}")
        return []

    try:
        encodings = ["utf-8-sig", "utf-8", "cp1256"]
        content = None
        for encoding in encodings:
            try:
                with open(csv_path, "r", encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            logger.error("لم نتمكن من قراءة الملف بأي ترميز")
            return []

        reader = csv.reader(content.strip().splitlines())
        header = next(reader, None)

        for row in reader:
            if len(row) >= 2:
                name = row[0].strip()
                phone = row[1].strip()
                phone = format_saudi_phone(phone)
                department = row[2].strip() if len(row) >= 3 else ""
                if name and phone:
                    recipients.append({"name": name, "phone": phone, "department": department})

        logger.info(f"تم تحميل {len(recipients)} مستلم من {csv_path}")
    except Exception as e:
        logger.error(f"خطأ في قراءة CSV: {e}")

    return recipients


# ============================================================
# حفظ المدعوين (لاستخدام Webhook)
# ============================================================

def register_invitees(recipients):
    """حفظ المدعوين في ملف JSON ليتعرف عليهم Webhook"""
    invitees = load_invitees()
    existing_phones = {inv["phone"] for inv in invitees}

    added = 0
    for r in recipients:
        if r["phone"] not in existing_phones:
            invitees.append({
                "name": r["name"],
                "phone": r["phone"],
                "department": r.get("department", ""),
                "invited_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            existing_phones.add(r["phone"])
            added += 1

    save_invitees(invitees)
    if added > 0:
        logger.info(f"  📋 تم تسجيل {added} مدعو جديد في قاعدة البيانات")


# ============================================================
# إرسال جماعي
# ============================================================

def send_to_recipients(client, recipients, content_sid=None):
    total = len(recipients)
    success_count = 0
    fail_count = 0
    buttons_count = 0
    text_count = 0
    results = []

    # حفظ المدعوين
    register_invitees(recipients)

    logger.info(f"\n{'=' * 50}")
    logger.info(f"بدء إرسال {total} دعوة تفاعلية")
    logger.info(f"{'=' * 50}\n")

    for i, recipient in enumerate(recipients, 1):
        name = recipient["name"]
        phone = recipient["phone"]
        department = recipient.get("department", "")

        logger.info(f"[{i}/{total}] إرسال إلى: {name} ({phone})")

        success, result, msg_type = send_invitation(client, phone, name, content_sid, department)

        if success:
            success_count += 1
            if msg_type == "buttons":
                buttons_count += 1
            else:
                text_count += 1
            logger.info(f"  ✅ تم الإرسال ({msg_type}) - SID: {result}")
            results.append({"name": name, "phone": phone, "status": "نجاح", "type": msg_type, "sid": result})
        else:
            fail_count += 1
            logger.error(f"  ❌ فشل الإرسال - {result}")
            results.append({"name": name, "phone": phone, "status": "فشل", "type": "error", "detail": result})

        if i < total:
            time.sleep(DELAY_BETWEEN_MESSAGES)

    logger.info(f"\n{'=' * 50}")
    logger.info(f"ملخص الإرسال:")
    logger.info(f"  إجمالي:     {total}")
    logger.info(f"  نجاح:       {success_count} ✅")
    logger.info(f"    بأزرار:   {buttons_count}")
    logger.info(f"    نصية:     {text_count}")
    logger.info(f"  فشل:        {fail_count} ❌")
    logger.info(f"{'=' * 50}")

    save_results(results)


def save_results(results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"send_results_{timestamp}.csv"

    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "phone", "status", "type", "sid", "detail"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "name": r.get("name", ""),
                "phone": r.get("phone", ""),
                "status": r.get("status", ""),
                "type": r.get("type", ""),
                "sid": r.get("sid", ""),
                "detail": r.get("detail", "")
            })

    logger.info(f"تم حفظ النتائج في: {filename}")


# ============================================================
# القائمة الرئيسية
# ============================================================

def main_menu():
    print()
    print("=" * 55)
    print("  🎓 نظام إرسال دعوات واتساب التفاعلي")
    print("  الكلية التقنية بالأحساء")
    print("=" * 55)

    # الاتصال بـ Twilio
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        print("\n  ✅ تم الاتصال بـ Twilio بنجاح")
    except Exception as e:
        print(f"\n  ❌ فشل الاتصال بـ Twilio: {e}")
        return

    # إعداد القالب التفاعلي
    print("\n  ⏳ جاري إعداد القالب التفاعلي...")
    content_sid = setup_content_template(client)

    if content_sid:
        print(f"  ✅ القالب جاهز - الدعوات ستُرسل بأزرار تفاعلية")
    else:
        print(f"  ℹ️  سيتم إرسال رسائل نصية مع تعليمات الرد")

    while True:
        print()
        print("─" * 55)
        print(f"  الفعالية: {EVENT_NAME}")
        print(f"  التاريخ:  {EVENT_DATE} | الوقت: {EVENT_TIME}")
        print("─" * 55)
        print()
        print("  1. 📋 عرض قائمة المدعوين")
        print("  2. 🧪 إرسال رسالة اختبار (لرقمك)")
        print("  3. 📨 إرسال دعوة لشخص واحد")
        print("  4. 📤 إرسال جماعي من ملف CSV")
        print("  5. 📤 إرسال جماعي من القائمة المحفوظة")
        print("  6. 🔄 إعادة إنشاء القالب التفاعلي")
        print("  7. 📊 عرض الردود المحفوظة")
        print("  0. 🚪 خروج")
        print()

        choice = input("  اختر رقم العملية: ").strip()

        if choice == "1":
            show_invitee_list()

        elif choice == "2":
            send_test(client, content_sid)

        elif choice == "3":
            send_single(client, content_sid)

        elif choice == "4":
            recipients = load_recipients_csv(CSV_FILE)
            if recipients:
                print(f"\n  سيتم إرسال {len(recipients)} دعوة من ملف CSV:")
                for r in recipients:
                    print(f"    - {r['name']} ({r['phone']})")
                confirm = input("\n  متأكد؟ (نعم/لا): ").strip()
                if confirm in ["نعم", "y", "yes"]:
                    send_to_recipients(client, recipients, content_sid)
            else:
                print(f"\n  ⚠️ لا يوجد مستلمون في {CSV_FILE}")

        elif choice == "5":
            invitees = load_invitees()
            if invitees:
                recipients = []
                for inv in invitees:
                    phone = format_saudi_phone(inv["phone"])
                    if inv["name"] and phone:
                        recipients.append({"name": inv["name"], "phone": phone, "department": inv.get("department", "")})

                print(f"\n  سيتم إرسال {len(recipients)} دعوة:")
                for r in recipients:
                    print(f"    - {r['name']} ({r['phone']})")
                confirm = input("\n  متأكد؟ (نعم/لا): ").strip()
                if confirm in ["نعم", "y", "yes"]:
                    send_to_recipients(client, recipients, content_sid)
            else:
                print("\n  ⚠️ لا يوجد مدعوون محفوظون. أرسل من CSV أولاً.")

        elif choice == "6":
            # حذف القالب القديم وإنشاء جديد
            config = load_config()
            config.pop("content_sid", None)
            save_config(config)
            content_sid = setup_content_template(client)
            if content_sid:
                print(f"\n  ✅ تم إنشاء قالب جديد: {content_sid}")
            else:
                print(f"\n  ℹ️  سيتم استخدام الرسائل النصية")

        elif choice == "7":
            show_responses()

        elif choice == "0":
            print("\n  شكراً لاستخدام النظام! 👋")
            break

        else:
            print("\n  ❌ اختيار غير صحيح")


def show_invitee_list():
    """عرض قائمة المدعوين"""
    print(f"\n{'=' * 50}")

    # من ملف JSON
    invitees = load_invitees()
    if invitees:
        print(f"  المدعوون المحفوظون ({len(invitees)}):")
        for i, inv in enumerate(invitees, 1):
            print(f"    {i}. {inv['name']} | {inv['phone']} | {inv.get('department', '-')}")
    else:
        print("  لا يوجد مدعوون محفوظون بعد")

    # من ملف CSV
    if os.path.exists(CSV_FILE):
        csv_recipients = load_recipients_csv(CSV_FILE)
        if csv_recipients:
            print(f"\n  ملف CSV ({CSV_FILE}) - {len(csv_recipients)} مدعو:")
            for i, r in enumerate(csv_recipients, 1):
                print(f"    {i}. {r['name']} | {r['phone']}")

    print(f"{'=' * 50}")


def send_test(client, content_sid):
    """إرسال رسالة اختبار"""
    print("\n  أدخل رقم جوالك للاختبار:")
    phone = input("  رقم الجوال (05XXXXXXXX): ").strip()
    phone = format_saudi_phone(phone)

    if not phone:
        print("  ❌ رقم غير صحيح!")
        return

    name = input("  اسمك (للاختبار): ").strip() or "اختبار"

    print(f"\n  ⏳ جاري الإرسال...")
    success, result, msg_type = send_invitation(client, phone, name, content_sid)

    if success:
        print(f"\n  ✅ تم الإرسال بنجاح ({msg_type})")
        print(f"  SID: {result}")
        if msg_type == "buttons":
            print(f"  💡 ستظهر أزرار تأكيد/اعتذار في واتساب")
        else:
            print(f"  💡 رد بـ 'تأكيد' أو 'اعتذار' لاختبار Webhook")
    else:
        print(f"\n  ❌ فشل الإرسال: {result}")


def send_single(client, content_sid):
    """إرسال دعوة لشخص واحد"""
    print("\n  أدخل بيانات المدعو:")
    name = input("  الاسم: ").strip()
    phone = input("  رقم الجوال (05XXXXXXXX): ").strip()
    department = input("  القسم (اختياري): ").strip()

    if not name or not phone:
        print("  ❌ بيانات ناقصة!")
        return

    phone = format_saudi_phone(phone)
    if not phone:
        print("  ❌ رقم غير صحيح!")
        return

    # تسجيل المدعو
    register_invitees([{"name": name, "phone": phone, "department": department}])

    print(f"\n  ⏳ جاري الإرسال...")
    success, result, msg_type = send_invitation(client, phone, name, content_sid, department)

    if success:
        print(f"\n  ✅ تم إرسال الدعوة إلى {name} ({msg_type})")
        print(f"  SID: {result}")
    else:
        print(f"\n  ❌ فشل الإرسال: {result}")


def show_responses():
    """عرض الردود المحفوظة"""
    responses_file = "responses.json"
    if not os.path.exists(responses_file):
        print("\n  📭 لا توجد ردود بعد")
        print("  💡 تأكد من تشغيل webhook_server.py لاستقبال الردود")
        return

    with open(responses_file, "r", encoding="utf-8") as f:
        responses = json.load(f)

    if not responses:
        print("\n  📭 لا توجد ردود بعد")
        return

    accepted = [r for r in responses if r.get("status") == "تأكيد حضور"]
    declined = [r for r in responses if r.get("status") == "اعتذار"]

    print(f"\n{'=' * 50}")
    print(f"  📊 ملخص الردود")
    print(f"{'=' * 50}")
    print(f"  إجمالي الردود:  {len(responses)}")
    print(f"  تأكيد حضور:     {len(accepted)} ✅")
    print(f"  اعتذار:          {len(declined)} ❌")
    print(f"{'=' * 50}")

    for r in responses:
        icon = "✅" if r.get("status") == "تأكيد حضور" else "❌"
        print(f"  {icon} {r.get('name', '-')} | {r.get('phone', '-')} | {r.get('timestamp', '-')}")

    print(f"{'=' * 50}")


# ============================================================
# التشغيل
# ============================================================

if __name__ == "__main__":
    main_menu()
