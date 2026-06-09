# تدقيق الروابط — بطاقة قاضي

**تاريخ التدقيق:** 2026-06-09
**الملف المدقق:** `outputs/test_card_001_qadi.md`
**المرجع الحاكم:** `outputs/LINK_VALIDATION_LOCK.md`
**نتيجة --final:** ✅ اجتاز
**مرجع الاعتماد:** commit `962337a`
**الحالة:** ✅ **معتمدة نهائيًا — التحقق اليدوي مكتمل**

---

## إحصائيات الفحص

| البند | القيمة |
|-------|--------|
| إجمالي الروابط | 12 |
| مقبول | 12 |
| يحتاج مراجعة | 0 |
| BLOCKED (مرفوض نهائيًا) | 0 |

---

## تفاصيل الروابط

| # | النص | الرابط | الحالة | ملاحظة |
|---|------|--------|--------|--------|
| 1 | الدبلوم العالي في القضاء والسياسة الشرعية | https://iu.edu.sa/Program-law5 | ✅ مقبول | رابط مباشر، بدون query params |
| 2 | الدبلوم العالي في الفقه | https://islp.kku.edu.sa/ar/node/670 | ✅ مقبول | رابط مباشر، بدون query params |
| 3 | الدبلوم العالي للعلوم القانونية | https://www.ipa.edu.sa/ar/training/law-diploma | ✅ مقبول | رابط مباشر، بدون query params |
| 4 | نظام الأحوال الشخصية | https://ethrai.sa/course-details/نظام-الأحوال-الشخصية | ✅ مقبول | رابط دورة مباشر على إثرائي |
| 5 | Think Again I: How to Understand Arguments | https://www.coursera.org/learn/understanding-arguments | ✅ مقبول | /learn/slug — صيغة Coursera المعتمدة — بديل A Law Student's Toolkit |
| 6 | قضاء التنفيذ | https://ethrai.sa/course-details/eb5b9ea5-3261-ea11-80d7-0050568c1fee | ✅ مقبول | رابط دورة مباشر على إثرائي |
| 7 | المرافعات أمام الجهات الشرعية | https://ethrai.sa/course-details/bbbfe41e-9487-ea11-80db-0050568c2944 | ✅ مقبول | رابط دورة مباشر على إثرائي — بديل An Introduction to American Law |
| 8 | Challenging Forensic Science | https://www.coursera.org/learn/challenging-forensic-science | ✅ مقبول | /learn/slug — صيغة Coursera المعتمدة |
| 9 | شهادة CAMS | https://www.acams.org/en/certifications/cams-certification | ✅ مقبول | رابط صفحة شهادة رسمية |
| 10 | عضوية MCIArb | https://www.ciarb.org/membership/routes-to-membership/member/ | ✅ مقبول | رابط صفحة عضوية رسمية |
| 11 | شهادة CSAA | https://aaoifi.com/apply-for-csaa/ | ✅ مقبول | **تم تصحيحه** — أُزيل `?lang=en` |
| 12 | شهادة CFE | https://www.acfe.com/cfe-credential/how-to-earn-your-cfe-credential | ✅ مقبول | رابط صفحة شهادة رسمية |

---

## تصحيحات أُجريت

| الرابط | المشكلة | التصحيح |
|--------|---------|---------|
| CSAA — https://aaoifi.com/apply-for-csaa/ | كان يحتوي `?lang=en` (BLOCKED_QUERY_PARAMS) | حُذف query parameter — الرابط نظيف |

---

## قيد بيئة التنفيذ — موثّق ومعتمد

الفحص الآلي بـHTTP من بيئة السحابة يعود بـ403 على جميع المواقع بسبب حجب IP السحابي (anti-bot protection). هذا **لا يُعد فشلاً للرابط** — بل قيد تقني للبيئة لا علاقة له بصحة الروابط.

**التحقق اليدوي:** تم خارجيًا بتاريخ 2026-06-09 — جميع الروابط الـ12 تفتح مباشرة في المتصفح.

| الرابط | نتيجة التحقق اليدوي |
|--------|---------------------|
| iu.edu.sa/Program-law5 | ✅ يفتح |
| islp.kku.edu.sa/ar/node/670 | ✅ يفتح |
| ipa.edu.sa/ar/training/law-diploma | ✅ يفتح |
| ethrai.sa — نظام الأحوال الشخصية | ✅ يفتح |
| coursera.org/learn/understanding-arguments | ✅ يفتح |
| ethrai.sa — قضاء التنفيذ | ✅ يفتح |
| ethrai.sa — المرافعات أمام الجهات الشرعية | ✅ يفتح |
| coursera.org/learn/challenging-forensic-science | ✅ يفتح |
| acams.org/en/certifications/cams-certification | ✅ يفتح |
| ciarb.org/.../member/ | ✅ يفتح |
| aaoifi.com/apply-for-csaa/ | ✅ يفتح |
| acfe.com/.../how-to-earn-your-cfe-credential | ✅ يفتح |

---

## نتيجة --final

```
✅ الملف اجتاز LINK_VALIDATION_LOCK — لا توجد روابط مرفوضة نهائيًا.
```
