# Verified Link Registry — سجل الروابط المعتمدة
**الإصدار:** v2.1 — SMART LINK RESOLUTION ENGINE + LINK TYPE BOUNDARY LOCK  
**آخر تحديث:** 2026-06-15  
**القاعدة:** السجل **Cache ذكي**، ليس whitelist مغلقًا. أي رابط جديد يُحلَّل تلقائيًا ويُرقَّى إلى HIGH_VERIFIED أو يُستبدَل دون تدخل المستخدم.

---

## القواعد الإلزامية

```
السجل ليس whitelist مغلقًا؛ السجل Cache ذكي.
أي رابط جديد يُحلَّل تلقائيًا عبر SMART LINK RESOLUTION ENGINE ويُرقَّى إلى HIGH_VERIFIED أو يُستبدَل — دون تدخل المستخدم.

ممنوع إدراج رابط حرج بدرجة MEDIUM أو UNKNOWN أو NOT_VERIFIED أو NEEDS_RESOLUTION.
ممنوع تخمين URL من نمط متوقع دون دليل WebSearch مؤكد.
ممنوع استخدام صفحة رئيسية عامة أو صفحة كلية أو صفحة منصة عامة.
ممنوع استخدام رابط يتطلب تسجيل دخول.
إذا الرابط غير موجود في السجل → يشغّل SMART LINK RESOLUTION ENGINE تلقائيًا.
إذا فشل الاكتشاف → استبدل المحتوى ببديل يملك رابطًا HIGH_VERIFIED.
المستخدم لا يراجع الروابط يدويًا — النظام مسؤول كامل.

الرابط الصحيح في النوع الخطأ = رابط مرفوض.
HIGH_VERIFIED وحده لا يكفي — يجب أن يطابق نوع الرابط [type] نوع القسم الذي أُدرج فيه.
```

### LINK TYPE BOUNDARY LOCK v1.0 — قواعد مطابقة النوع

| القسم | الأنواع المقبولة | مثال على خلط مرفوض |
|---|---|---|
| برامج التأهيل المعتمدة | `program`, `diploma`, `degree` | SHRM-CP = TYPE_MISMATCH |
| الشهادات المهنية الاحترافية | `certification` | ICA Diploma في الشهادات = TYPE_MISMATCH |
| الدورات الداعمة | `course` (Coursera/إثرائي/دروب) | edX = COURSE_PLATFORM_NOT_ALLOWED |

**أنواع الأخطاء:** `TYPE_MISMATCH` \| `COURSE_PLATFORM_NOT_ALLOWED` \| `DUPLICATE_ENTITY_ACROSS_SECTIONS` \| `UNKNOWN_TYPE`

## حالات الروابط في السجل

| الحالة | المعنى | مسموح في البطاقات؟ |
|--------|--------|-------------------|
| **HIGH_VERIFIED** | مثبت بـ WebSearch أو مرجع رسمي | ✅ نعم |
| **MEDIUM_VERIFIED** | موجود في البطاقات القديمة فقط | ❌ لا |
| **REJECTED** | مرفوض مع سبب موثق | ❌ لا |
| **NOT_VERIFIED** | غير مثبت أو فشل | ❌ لا |

## مسار حل الرابط التلقائي (SMART LINK RESOLUTION ENGINE)

```
رابط جديد في البطاقة
    ↓
هل هو في السجل؟
    ├─ HIGH_VERIFIED → ✅ قبول مباشر
    ├─ REJECTED / NOT_VERIFIED → ❌ استبدال إلزامي
    └─ UNKNOWN / غير موجود
         ↓
         SMART LINK RESOLUTION ENGINE
         [smart_link_resolver.py resolve --url X --name Y --title T --snippet S]
              ↓
         هل الصفحة محددة (ليست homepage)؟ + هل الاسم ظاهر في النتيجة؟
              ├─ نعم → DISCOVERED → أُضيف للسجل → HIGH_VERIFIED → ✅
              └─ لا  → ابحث عن بديل
                       ├─ وُجد بديل HIGH_VERIFIED → استبدل → ✅
                       └─ لا بديل → غيّر المحتوى → ✅
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
| التفاوض الناجح | Successful Negotiation | `coursera.org/learn/negotiation-skills` | University of Michigan / Coursera | **WebSearch CONFIRMED** — اكتشفه ENGINE تلقائيًا 2026-06-15 |
| برنامج القراءة — iRead | iRead Program | `ithra.com/en/special-programs/iread` | Ithra / مركز الملك عبدالعزيز | **WebSearch CONFIRMED** — اكتشفه ENGINE تلقائيًا 2026-06-15 |

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
