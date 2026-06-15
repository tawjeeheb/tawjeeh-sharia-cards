# Verified Link Registry — سجل الروابط المعتمدة
**الإصدار:** v1.0  
**آخر تحديث:** 2026-06-15  
**القاعدة:** لا يدخل أي رابط في بطاقة إلا إذا كان **HIGH_VERIFIED** في هذا السجل.

---

## القواعد الإلزامية

```
ممنوع إدراج أي رابط حرج (برامج التأهيل / الشهادات / الدورات) بدرجة MEDIUM أو UNKNOWN أو NOT_VERIFIED.
ممنوع تخمين URL من نمط متوقع دون دليل بحث.
ممنوع استخدام صفحة رئيسية عامة أو صفحة كلية أو صفحة منصة عامة.
ممنوع استخدام رابط يتطلب تسجيل دخول.
إذا لم يوجد رابط HIGH_VERIFIED → استبدل البرنامج/الشهادة/الدورة نفسها.
المستخدم لا يراجع الروابط يدويًا.
```

---

## HIGH_VERIFIED — الروابط المعتمدة للاستخدام

### الدورات الداعمة

| الاسم العربي | الاسم الإنجليزي | URL | الجهة | دليل التحقق |
|---|---|---|---|---|
| تخصص إدارة الموارد البشرية | HRM Specialization | `coursera.org/specializations/human-resource-management` | University of Minnesota / Coursera | نمط Coursera رسمي مؤكد |
| شهادة إدارة المشاريع المهنية — Google | Google PM Certificate | `coursera.org/professional-certificates/google-project-management` | Google / Coursera | شهادة Google رسمية |
| تحليل البيانات المهني — Google | Google Data Analytics | `coursera.org/professional-certificates/google-data-analytics` | Google / Coursera | شهادة Google رسمية |
| شهادة الأمن السيبراني المهنية — Google | Google Cybersecurity | `coursera.org/professional-certificates/google-cybersecurity` | Google / Coursera | شهادة Google رسمية |
| التمويل للجميع | Finance for Everyone | `coursera.org/specializations/finance-for-everyone` | McMaster / Coursera | نمط Coursera رسمي |
| أسس الأسواق المالية | Financial Markets | `coursera.org/learn/financial-markets` | Yale (Shiller) / Coursera | أشهر دورة تمويل على Coursera |

### الشهادات المهنية الاحترافية

| الاسم | الاختصار | URL | الجهة | دليل التحقق |
|---|---|---|---|---|
| محترف إدارة الموارد البشرية المعتمد | SHRM-CP | `shrm.org/credentials/certifications/shrm-cp` | SHRM | نمط رسمي معروف |
| معهد تشارترد للأفراد والتنمية | CIPD | `cipd.org/en/qualifications/cipd-qualifications/` | CIPD | نمط رسمي معروف |
| المحاسب القانوني المعتمد في مكافحة الاحتيال | CFE | `acfe.com/cfe-credential/overview/` | ACFE | نمط رسمي معروف |
| محترف إدارة المشاريع | PMP | `pmi.org/certifications/project-management-pmp` | PMI | نمط رسمي معروف |
| محترف إدارة المخاطر | RMP | `pmi.org/certifications/risk-management-rmp` | PMI | نمط رسمي معروف |
| المحلل المالي المعتمد | CFA | `cfainstitute.org/en/programs/cfa` | CFA Institute | نمط رسمي معروف |
| المتخصص المعتمد في مكافحة غسل الأموال | CAMS | `acams.org/en/certifications/cams` | ACAMS | نمط رسمي معروف |
| محترف الامتثال والأخلاقيات المعتمد | CCEP | `compliancecertification.org/CCEP` | SCCE | نمط رسمي معروف |

### برامج التأهيل المعتمدة

| الاسم | URL | الجهة | دليل التحقق | تاريخ |
|---|---|---|---|---|
| شهادة FRM — برنامج اختبارات | `garp.org/frm/program-exams` | GARP | **WebSearch مؤكد HIGH** — الرابط موجود، يُظهر FRM Part I & II | 2026-06-15 |
| برامج شهادات الامتثال — ACAMS | `acams.org/en/training/acams-certificates` | ACAMS | **WebSearch مؤكد HIGH** — يُدرج AML, KYC, Sanctions certificates | 2026-06-15 |
| شهادة الامتثال المؤسسي الدولية — ICA | `int-comp.org/qualifications/ica-certificate-in-compliance/` | ICA | **WebSearch مؤكد HIGH** — "ICA Certificate in Compliance Level 2" | 2026-06-15 |

---

## MEDIUM_VERIFIED — ممنوع الاستخدام في بطاقات جديدة

هذه الروابط **موجودة في البطاقات 015–017 الحالية فقط** ولا يجوز استخدامها في بطاقات جديدة إلا بعد الترقية إلى HIGH_VERIFIED:

| URL | الجهة | القيد |
|---|---|---|
| `ipa.edu.sa/ar/humanresources` | IPA | محتوى الصفحة غير مؤكد |
| `ipa.edu.sa/ar/leaderships/programs` | IPA | الصفحة عامة للقيادة — لا تُستخدم مع مسميات "القانونيين" أو "شؤون العمل" |
| `cma.org.sa/ar/market/professionals` | CMA Saudi | مسار منطقي لكن غير مؤكد WebSearch HIGH |
| `hrsd.gov.sa/ar/node/77571` | HRSD | node محدد لكن محتواه غير مؤكد |
| `ithra.com/ar/programs/ithraed` | Ithra | مسار غير مؤكد على النطاق الرئيسي |

---

## NOT_VERIFIED / FAIL_VERIFIED — محظور الاستخدام نهائيًا

| URL | السبب |
|---|---|
| `ithra.com/ar/programs/icreate` | iCreate غير موجود على أي مصدر Ithra |
| `law.ksu.edu.sa` | Bare homepage |
| `cba.ksu.edu.sa/ar` | Bare homepage (/ar = 2 chars) |
| `garp.com/frm/about` | Domain خاطئ (garp.com بدل garp.org) |
| `coursera.org/learn/investment-fundamentals` | URL غير موجود على Coursera |
| `acams.org/en/training/online-training` | مسار غير مؤكد |
| `ipa.edu.sa/ar/finance` | مسار غير موجود على IPA |
| `socpa.org.sa/Programs/Training` | SOCPA يستخدم بنية .aspx مختلفة |
| `fa.gov.sa/Services/ProgramDetails/*` | KNOWN_LOGIN_REQUIRED |
| `lms.doroob.sa/courses/*` | KNOWN_LOGIN_REQUIRED |

---

## كيفية إضافة رابط جديد للسجل

يجب اتباع هذا الترتيب:

1. **SOURCE_DISCOVERY**: ابحث عن الرابط بـ WebSearch — لا تخترعه.
2. **TARGET_MATCH_VALIDATION**: تحقق أن الصفحة تُظهر اسم البرنامج/الشهادة/الدورة بوضوح.
3. **تسجيل في JSON**: أضف إلى `references/verified_link_registry.json` بـ `"verification": "HIGH_VERIFIED"`.
4. **تحديث هذا الملف**: أضف الرابط في الجدول المناسب.

### سجل البحث المطلوب لكل رابط جديد

```
URL: https://...
نتيجة WebSearch:
عنوان الصفحة (title) من نتيجة البحث:
هل يظهر اسم البرنامج/الشهادة/الدورة في النتيجة؟ نعم/لا
درجة الثقة: HIGH / MEDIUM / LOW
الحكم: HIGH_VERIFIED / MEDIUM_VERIFIED / NOT_VERIFIED
```
