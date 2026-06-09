# تدقيق الروابط — بطاقة قاضي

**تاريخ التدقيق:** 2026-06-09
**الملف المدقق:** `outputs/test_card_001_qadi.md`
**المرجع الحاكم:** `outputs/LINK_VALIDATION_LOCK.md`
**نتيجة --final:** ✅ اجتاز

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
| 5 | A Law Student's Toolkit | https://www.coursera.org/learn/law-student | ✅ مقبول | /learn/slug — صيغة Coursera المعتمدة |
| 6 | قضاء التنفيذ | https://ethrai.sa/course-details/eb5b9ea5-3261-ea11-80d7-0050568c1fee | ✅ مقبول | رابط دورة مباشر على إثرائي |
| 7 | An Introduction to American Law | https://www.coursera.org/learn/american-law | ✅ مقبول | /learn/slug — صيغة Coursera المعتمدة |
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

## ملاحظة: قيد بيئة التنفيذ

الفحص الآلي بـHTTP من بيئة السحابة يعود بـ403 على **جميع** المواقع بسبب حجب IP السحابي (anti-bot protection). هذا ليس دليلاً على كسر الروابط — بل قيد تقني للبيئة.

**التحقق اليدوي الإلزامي قبل الإخراج النهائي:**
افتح كل رابط في نافذة Incognito وتحقق من:
- [ ] iu.edu.sa/Program-law5 — يفتح صفحة الدبلوم مباشرة
- [ ] islp.kku.edu.sa/ar/node/670 — يفتح صفحة الدبلوم مباشرة
- [ ] ipa.edu.sa/ar/training/law-diploma — يفتح صفحة الدبلوم مباشرة
- [ ] ethrai.sa دورة الأحوال الشخصية — يفتح صفحة الدورة
- [ ] coursera.org/learn/law-student — يفتح صفحة الدورة
- [ ] ethrai.sa دورة قضاء التنفيذ — يفتح صفحة الدورة
- [ ] coursera.org/learn/american-law — يفتح صفحة الدورة
- [ ] coursera.org/learn/challenging-forensic-science — يفتح صفحة الدورة
- [ ] acams.org/en/certifications/cams-certification — يفتح صفحة الشهادة
- [ ] ciarb.org/.../member/ — يفتح صفحة العضوية
- [ ] aaoifi.com/apply-for-csaa/ — يفتح صفحة الشهادة
- [ ] acfe.com/.../how-to-earn-your-cfe-credential — يفتح صفحة الشهادة

---

## نتيجة --final

```
✅ الملف اجتاز LINK_VALIDATION_LOCK — لا توجد روابط مرفوضة نهائيًا.
```
