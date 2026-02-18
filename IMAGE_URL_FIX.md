# إصلاح: الدعوة مع الصورة لا تصل

## السبب
رابط الصورة مُخزَّن داخل القالب في Twilio. إذا كان الرابط من **GitHub** (raw.githubusercontent.com) أو من سيرفر **ينام** (مثل Render المجاني)، قد يرفض واتساب القالب أو لا تصل الرسالة.

---

## رفض القالب: "Error downloading invalid media URL: Unexpected end of file from server"

هذا يعني أن **خوادم واتساب لم تستطع تحميل الصورة** من الرابط (السيرفر أوقف الاتصال أو كان نائماً، مثلاً Render المجاني).

### الحل الموصى به: استضافة الصورة على خدمة ثابتة

يجب أن يكون **رابط الصورة يعمل 24/7** ولا يعتمد على سيرفر ينام. جرّب أحد الخيارات:

1. **Imgur** (مجاني)
   - اذهب إلى [imgur.com](https://imgur.com) → Upload → ارفع `job_fair_image.png`.
   - بعد الرفع اختر **Copy link** ثم احصل على **رابط الصورة المباشر** (مثل `i.imgur.com/xxxxx.png`).  
   - استخدم هذا الرابط في حقل **Media URL** في القالب.

2. **PostImages** أو **ImgBB** أو أي استضافة صور تعطيك رابطاً مباشراً (ينتهي بـ .png).

3. **رابط عام من GitHub** (أحياناً يعمل لبعض الحسابات):  
   `https://raw.githubusercontent.com/harbib-989/whatsapp-invitation-system/main/job_fair_image.png`  
   إذا رُفض مرة أخرى، استخدم Imgur أو بديله.

### بعد الحصول على الرابط الجديد

1. في Twilio: **Duplicate** القالب المرفوض (نسخ القالب).
2. في القالب الجديد غيّر **Media URL** إلى رابط الصورة الجديد (Imgur أو غيره).
3. احفظ ثم **Submit for WhatsApp approval**.
4. بعد الموافقة، ضع **Content template SID** الجديد في `config.json` → `content_sid_vip_card`.

---

## إذا كان الرابط من تطبيقك (Render / ngrok)

- **Render (مجاني):** السيرفر قد ينام، فخوادم واتساب قد تفشل في تحميل الصورة عند المراجعة. الأفضل استخدام Imgur أعلاه للقالب.
- **Render (مدفوع)** أو **ngrok:** يمكن تجربة الرابط إذا كان السيرفر يعمل باستمرار.

---

## خطأ: "Please add a header, a footer, or buttons"

تأكد أن البطاقة تحتوي على **ثلاثة أشياء**: Body + (Header **أو** Footer **أو** Buttons). اتبع التالي:

1. **Header (Media)**  
   - نوع: **Media**  
   - Media URL: `https://whatsapp-invitation-system.onrender.com/media/job_fair_image.png`  
   - إن كان الحقل فارغاً أو فيه خطأ، الصق الرابط من جديد ثم انقر خارج الحقل.

2. **Footer**  
   - اكتب نصاً (حتى 60 حرفاً)، مثلاً:  
     `الكلية التقنية بالأحساء | المؤسسة العامة للتدريب التقني`

3. **Buttons**  
   - زر 1: النص «تأكيد الحضور»، ID: `confirm_attendance`  
   - زر 2: النص «اعتذار عن الحضور»، ID: `decline_attendance`

4. **حفظ**  
   - اضغط **Save**. أحياناً الرسالة تختفي بعد الحفظ.  
   - إن استمرت: جرّب حذف رابط الـ Header ثم إعادة لصقه وحفظ مرة أخرى.

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

---

## إذا أنشأت قالباً جديداً (مثل copy_technicalcompetenciesforum)

1. اضغط **Save and submit for WhatsApp approval** في Twilio.
2. انتظر موافقة واتساب (قد تستغرق دقائق أو ساعات).
3. بعد الموافقة، انسخ **Content template SID** (يبدأ بـ `HX...`) من صفحة القالب في Twilio.
4. ضع الـ SID في `config.json`:
   ```json
   "content_sid_vip_card": "HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```
5. إذا التطبيق يعمل على Render، أضف نفس القيمة في **Environment**:
   `CONTENT_SID_VIP_CARD` = الـ SID الجديد.
