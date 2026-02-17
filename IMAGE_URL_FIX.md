# إصلاح: الدعوة مع الصورة لا تصل

## السبب
رابط الصورة مُخزَّن داخل القالب في Twilio. إذا كان الرابط من **GitHub** (raw.githubusercontent.com) فإن Twilio غالباً **لا يستطيع جلب الصورة** فيصبح الإرسال فاشلاً أو لا تصل الرسالة.

## الحل
استخدم رابط الصورة من تطبيقك (يعمل مع واتساب):

### إذا الموقع منشور على Render
```
https://whatsapp-invitation-system.onrender.com/media/job_fair_image.png
```

### إذا تشغّل محلياً مع ngrok
استخدم الرابط الذي يظهر في لوحة التحكم عند اختيار "بطاقة مع صورة" (مثل: `https://xxxx.ngrok-free.app/media/job_fair_image.png`).

---

## الخطوات في Twilio

1. ادخل إلى **Twilio Console** → **Messaging** → **Content** (أو **Try it out** → **Content**).
2. افتح القالب **technicalcompetenciesforum** (أو الاسم الظاهر عندك).
3. في **Configure Content - WhatsApp Card** → **Header** → **Media URL**:
   - احذف الرابط الحالي (GitHub).
   - الصق الرابط أعلاه (رابط Render أو ngrok).
4. احفظ التعديلات.
5. إذا طُلِب منك إعادة الموافقة من واتساب، اضغط **Submit for Approval**.

بعد ذلك أعد إرسال الدعوة (بطاقة مع صورة)؛ يفترض أن تصل إلى الجوالات.
