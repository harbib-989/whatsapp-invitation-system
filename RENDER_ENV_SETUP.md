# إعداد متغيرات البيئة على Render

على Render، الملفات `config.json` و `invitees.json` غير موجودة (لا تُرفع مع Git).
لذلك يجب تعيين المتغيرات التالية في **Render Dashboard → Service → Environment**:

## متغيرات مطلوبة (Twilio)

| المتغير | الوصف | مثال |
|---------|-------|------|
| `TWILIO_ACCOUNT_SID` | معرف حساب Twilio | ACxxxxxxxx... |
| `TWILIO_AUTH_TOKEN` | رمز المصادقة | your_auth_token |
| `TWILIO_FROM_PHONE` | رقم واتساب للارسال | whatsapp:+966550308539 |

## متغيرات اختيارية (نوع الفعالية)

| المتغير | القيم | الوصف |
|---------|-------|-------|
| `EVENT_MODE` | `dialogue` أو `job_fair` | نوع الفعالية - الافتراضي: `dialogue` |
| `CONTENT_SID` | SID القالب العام | مثال: HX5f92c7470551312f6d1d461f16dafdb6 |
| `CONTENT_SID_VIP` | قالب الدعوة الرسمية للمسؤولين | مثال: HXe8c0b79c33f7c9c1254f74c39ba547fb |

### EVENT_MODE = dialogue (افتراضي)
- **حوار: دور الرؤية في تعزيز الهوية الوطنية**
- التاريخ: الإثنين ٢١ شعبان ١٤٤٧هـ
- القالب: HX5f92c7470551312f6d1d461f16dafdb6

### EVENT_MODE = job_fair
- **ملتقى الكفاءات التقنية**
- نصائح: سيرة ذاتية، ملابس رسمية، مقابلات
- القالب: HX7f91572f7f87564aa0265dbe20b6ae12

## مثال إعداد ملتقى الكفاءات (مع القالب الرسمي)

```
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_PHONE=whatsapp:+966550308539
EVENT_MODE=job_fair
CONTENT_SID_VIP=HXe8c0b79c33f7c9c1254f74c39ba547fb
```

## ملاحظة
عند الإرسال من لوحة التحكم، يُضاف المدعو تلقائياً إلى `invitees.json` على السيرفر.
عند الرد على الدعوة، يستخدم النظام الاسم المحفوظ. إن لم يُعثر على المدعو يظهر "عزيزي المدعو" في الرد التلقائي.
