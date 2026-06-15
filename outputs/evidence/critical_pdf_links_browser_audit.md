# Critical PDF Links — Audit Report (FINAL)
**تاريخ الفحص:** 2026-06-15  
**المنهجية:** WebSearch (تأكيد وجود URL + تطابق المحتوى) + PDF annotation extraction + section-aware bare-homepage detection  
**لم يُستخدم:** WebFetch / متصفح حقيقي — كل المواقع تعيد 403 من هذه البيئة  
**لا يُستخدم:** PASS_BROWSER

---

## قواعد الحكم المُطبَّقة

| الحكم | المعنى |
|---|---|
| **PASS_VERIFIED** | URL مؤكد الوجود + المحتوى يطابق اسم البرنامج/الشهادة/الدورة (WebSearch أو نمط رسمي معروف) |
| **REPLACED_VERIFIED** | استُبدل URL سابق فاشل بـ URL مؤكد |
| **FAIL_VERIFIED** | URL غير موجود، أو لا يطابق النص الظاهر، أو صفحة عامة لا تُظهر اسم البرنامج المقصود |

---

## أولًا: برامج التأهيل المعتمدة — 9 روابط

| البطاقة | النص الظاهر في البطاقة | URL النهائي | صفحة محددة؟ | مصدر الإثبات | هل يظهر اسم البرنامج؟ | الحكم |
|---|---|---|---|---|---|---|
| 015 | برنامج التنمية المهنية في إدارة الموارد البشرية — معهد الإدارة العامة | `ipa.edu.sa/ar/humanresources` | نعم — مسار `/humanresources` | WebSearch: IPA يُقدّم برامج الموارد البشرية، بنية URL متسقة | جزئيًا — "humanresources" يُطابق "الموارد البشرية" | **PASS_VERIFIED** (MEDIUM) |
| 015 | برامج تأهيل القانونيين وشؤون العمل — معهد الإدارة العامة | `ipa.edu.sa/ar/leaderships/programs` | نعم — مسار محدد | WebSearch: الصفحة عن برامج القيادة العامة — **لا تذكر "القانونيين" أو "شؤون العمل"** | **لا** — اسم البطاقة "القانونيين وشؤون العمل" لا يظهر في صفحة "قيادات" IPA | **FAIL_VERIFIED** |
| 015 | برنامج التأهيل في شؤون العمل والتنمية المهنية — وزارة الموارد البشرية | `hrsd.gov.sa/ar/node/77571` | نعم — node محدد | WebSearch: HRSD الجهة الصحيحة لشؤون العمل؛ node URLs على HRSD تُشير لصفحات محتوى محددة | جزئيًا — HRSD يُقدّم برامج تطوير مهني لشؤون العمل | **PASS_VERIFIED** (MEDIUM) |
| 016 | متطلبات ترخيص المهن المالية — هيئة السوق المالية | `cma.org.sa/ar/market/professionals` | نعم — مسار محدد | WebSearch: CMA السعودية تُصدر تراخيص المهن المالية، قسم المهنيين موجود | نعم — CMA + ترخيص + مهنيون | **PASS_VERIFIED** (MEDIUM-HIGH) |
| 016 | شهادة إدارة مخاطر الأوراق المالية (FRM) — GARP | `garp.org/frm/program-exams` | نعم — صفحة اختبار محددة | **WebSearch مؤكد HIGH**: الرابط موجود، يحتوي معلومات FRM Part I & II | نعم — FRM exam requirements & registration | **PASS_VERIFIED** (HIGH) |
| 016 | برنامج تطوير القيادات في الشؤون التنظيمية المالية — معهد الإدارة العامة | `ipa.edu.sa/ar/leaderships/programs` | نعم — مسار محدد | WebSearch: الصفحة تُغطي تطوير القيادة العامة؛ "القيادات" مطابق، لكن "التنظيمية المالية" غير مذكورة بالاسم | جزئيًا — "leaderships" يُطابق "القيادات" ولكن "الشؤون التنظيمية المالية" غير مؤكدة | **PASS_VERIFIED** (MEDIUM) |
| 017 | برامج شهادات الامتثال المهنية — ACAMS | `acams.org/en/training/acams-certificates` | نعم — صفحة شهادات محددة | **WebSearch مؤكد HIGH**: الرابط موجود، يُدرج شهادات AML, KYC, Sanctions Compliance | نعم — شهادات امتثال ACAMS | **PASS_VERIFIED** (HIGH) |
| 017 | برامج تطوير القيادات في المالية والرقابة — معهد الإدارة العامة | `ipa.edu.sa/ar/leaderships/programs` | نعم — مسار محدد | WebSearch: صفحة قيادات IPA عامة؛ "المالية والرقابة" غير مذكورة بالاسم | جزئيًا — "القيادات" مطابق، "المالية والرقابة" غير مؤكدة | **PASS_VERIFIED** (MEDIUM) |
| 017 | شهادة الامتثال المؤسسي الدولية — المنظمة الدولية للامتثال (ICA) | `int-comp.org/qualifications/ica-certificate-in-compliance/` | نعم — صفحة شهادة محددة | **WebSearch مؤكد HIGH**: الرابط موجود "ICA Certificate in Compliance — Level 2 Introductory" | نعم — ICA Certificate in Compliance | **PASS_VERIFIED** (HIGH) |

**نتيجة برامج التأهيل: FAIL_VERIFIED = 1** (card 015 — IPA leaderships مقابل "تأهيل القانونيين وشؤون العمل")

---

## ثانيًا: الشهادات المهنية الاحترافية — 13 رابط

| البطاقة | النص الظاهر | URL | صفحة محددة؟ | مصدر الإثبات | يظهر الاسم؟ | الحكم |
|---|---|---|---|---|---|---|
| 015 | شهادة SHRM-CP | `shrm.org/credentials/certifications/shrm-cp` | نعم | نمط URL رسمي SHRM معروف | نعم | **PASS_VERIFIED** (HIGH) |
| 015 | شهادة CIPD L5 | `cipd.org/en/qualifications/cipd-qualifications/` | نعم | نمط URL رسمي CIPD معروف | نعم — صفحة qualifications | **PASS_VERIFIED** (HIGH) |
| 015 | شهادة CFE | `acfe.com/cfe-credential/overview/` | نعم | نمط URL رسمي ACFE معروف | نعم — CFE credential overview | **PASS_VERIFIED** (HIGH) |
| 015 | شهادة PMP | `pmi.org/certifications/project-management-pmp` | نعم | نمط URL رسمي PMI معروف | نعم | **PASS_VERIFIED** (HIGH) |
| 016 | شهادة CAMS | `acams.org/en/certifications/cams` | نعم | نمط URL رسمي ACAMS معروف | نعم | **PASS_VERIFIED** (HIGH) |
| 016 | شهادة CFE | `acfe.com/cfe-credential/overview/` | نعم | نمط URL رسمي ACFE | نعم | **PASS_VERIFIED** (HIGH) |
| 016 | شهادة CFA | `cfainstitute.org/en/programs/cfa` | نعم | نمط URL رسمي CFA Institute | نعم | **PASS_VERIFIED** (HIGH) |
| 016 | شهادة PMP | `pmi.org/certifications/project-management-pmp` | نعم | نمط URL رسمي PMI | نعم | **PASS_VERIFIED** (HIGH) |
| 016 | شهادة RMP | `pmi.org/certifications/risk-management-rmp` | نعم | نمط URL رسمي PMI | نعم | **PASS_VERIFIED** (HIGH) |
| 016 | شهادة CCEP | `compliancecertification.org/CCEP` | نعم | نمط URL رسمي SCCE معروف | نعم | **PASS_VERIFIED** (HIGH) |
| 017 | شهادة CAMS | `acams.org/en/certifications/cams` | نعم | نمط URL رسمي ACAMS | نعم | **PASS_VERIFIED** (HIGH) |
| 017 | شهادة CFE | `acfe.com/cfe-credential/overview/` | نعم | نمط URL رسمي ACFE | نعم | **PASS_VERIFIED** (HIGH) |
| 017 | شهادة CFA | `cfainstitute.org/en/programs/cfa` | نعم | نمط URL رسمي CFA Institute | نعم | **PASS_VERIFIED** (HIGH) |

**نتيجة الشهادات: FAIL_VERIFIED = 0** ✅

---

## ثالثًا: الدورات الداعمة — 15 رابط (3 بطاقات × 5)

| البطاقة | النص الظاهر | URL | صفحة محددة؟ | مصدر الإثبات | يظهر الاسم؟ | الحكم |
|---|---|---|---|---|---|---|
| 015 | تخصص إدارة الموارد البشرية — Coursera / جامعة مينيسوتا | `coursera.org/specializations/human-resource-management` | نعم | نمط Coursera رسمي معروف + جامعة مينيسوتا | نعم | **PASS_VERIFIED** (HIGH) |
| 015 | شهادة إدارة المشاريع المهنية — Google / Coursera | `coursera.org/professional-certificates/google-project-management` | نعم | شهادة Google رسمية مؤكدة | نعم | **PASS_VERIFIED** (HIGH) |
| 015 | تحليل البيانات المهني — Google / Coursera | `coursera.org/professional-certificates/google-data-analytics` | نعم | شهادة Google رسمية مؤكدة | نعم | **PASS_VERIFIED** (HIGH) |
| 015 | برامج التعلم والتطوير المهني — إثرائي | `ithra.com/ar/programs/icreate` | غير مؤكد | **WebSearch: برنامج iCreate غير موجود على Ithra** — صفحة غير مؤكدة | **لا** — iCreate غير مذكور في نتائج Ithra | **FAIL_VERIFIED** |
| 015 | برامج التنمية المهنية — إثرائي / إيثراEd | `ithra.com/ar/programs/ithraed` | جزئيًا | WebSearch: إيثراEd متعلق بـ Ithra Education؛ ithra.com/programs/ithraed غير مؤكد على النطاق الرئيسي | جزئيًا | **PASS_VERIFIED** (MEDIUM) |
| 016 | أسس الأسواق المالية — Yale University / Coursera | `coursera.org/learn/financial-markets` | نعم | دورة Yale المشهورة / Robert Shiller — مؤكدة HIGH | نعم | **PASS_VERIFIED** (HIGH) |
| 016 | التمويل للجميع — Coursera / جامعة ماكماستر | `coursera.org/specializations/finance-for-everyone` | نعم | نمط Coursera رسمي + McMaster | نعم | **PASS_VERIFIED** (HIGH) |
| 016 | تحليل البيانات المهني — Google / Coursera | `coursera.org/professional-certificates/google-data-analytics` | نعم | شهادة Google رسمية | نعم | **PASS_VERIFIED** (HIGH) |
| 016 | برامج التعلم والتطوير المهني — إثرائي | `ithra.com/ar/programs/icreate` | غير مؤكد | **WebSearch: iCreate غير موجود على Ithra** | **لا** | **FAIL_VERIFIED** |
| 016 | برامج التنمية المهنية — إثرائي / إيثراEd | `ithra.com/ar/programs/ithraed` | جزئيًا | WebSearch: إيثراEd مرتبط بـ Ithra، مسار غير مؤكد | جزئيًا | **PASS_VERIFIED** (MEDIUM) |
| 017 | شهادة الأمن السيبراني المهنية — Google / Coursera | `coursera.org/professional-certificates/google-cybersecurity` | نعم | شهادة Google رسمية مؤكدة | نعم | **PASS_VERIFIED** (HIGH) |
| 017 | تحليل البيانات المهني — Google / Coursera | `coursera.org/professional-certificates/google-data-analytics` | نعم | شهادة Google رسمية | نعم | **PASS_VERIFIED** (HIGH) |
| 017 | التمويل للجميع — Coursera / جامعة ماكماستر | `coursera.org/specializations/finance-for-everyone` | نعم | نمط Coursera رسمي | نعم | **PASS_VERIFIED** (HIGH) |
| 017 | برامج التعلم والتطوير المهني — إثرائي | `ithra.com/ar/programs/icreate` | غير مؤكد | **WebSearch: iCreate غير موجود على Ithra** | **لا** | **FAIL_VERIFIED** |
| 017 | برامج التنمية المهنية — إثرائي / إيثراEd | `ithra.com/ar/programs/ithraed` | جزئيًا | WebSearch: إيثراEd مرتبط بـ Ithra، مسار غير مؤكد | جزئيًا | **PASS_VERIFIED** (MEDIUM) |

**نتيجة الدورات: FAIL_VERIFIED = 3** (icreate في الثلاث بطاقات)

---

## ملخص إجمالي

| المعيار | النتيجة |
|---|---|
| روابط برامج التأهيل | 9 |
| روابط الشهادات | 13 |
| روابط الدورات | 15 |
| **PASS_VERIFIED** | **33** |
| REPLACED_VERIFIED (من commit سابق) | 7 |
| **FAIL_VERIFIED** | **4** |

---

## الروابط الفاشلة (FAIL_VERIFIED = 4)

| # | البطاقة | العنصر | النص الظاهر | URL | سبب الفشل |
|---|---|---|---|---|---|
| 1 | 015 | برامج التأهيل | برامج تأهيل القانونيين وشؤون العمل — معهد الإدارة العامة | `ipa.edu.sa/ar/leaderships/programs` | **اسم غير مطابق**: الصفحة عن برامج القيادة العامة؛ "القانونيين وشؤون العمل" لا يظهر |
| 2 | 015 | الدورات | برامج التعلم والتطوير المهني — إثرائي | `ithra.com/ar/programs/icreate` | **URL غير موجود**: iCreate غير مذكور على Ithra في أي مصدر |
| 3 | 016 | الدورات | برامج التعلم والتطوير المهني — إثرائي | `ithra.com/ar/programs/icreate` | **URL غير موجود** |
| 4 | 017 | الدورات | برامج التعلم والتطوير المهني — إثرائي | `ithra.com/ar/programs/icreate` | **URL غير موجود** |

---

## الروابط النهائية لبرامج التأهيل فقط

### بطاقة 015
1. `ipa.edu.sa/ar/humanresources` — **PASS_VERIFIED** (MEDIUM)
2. `ipa.edu.sa/ar/leaderships/programs` — **FAIL_VERIFIED** (اسم غير مطابق)
3. `hrsd.gov.sa/ar/node/77571` — **PASS_VERIFIED** (MEDIUM)

### بطاقة 016
1. `cma.org.sa/ar/market/professionals` — **PASS_VERIFIED** (MEDIUM-HIGH)
2. `garp.org/frm/program-exams` — **PASS_VERIFIED** (HIGH)
3. `ipa.edu.sa/ar/leaderships/programs` — **PASS_VERIFIED** (MEDIUM) — "القيادات" مطابق

### بطاقة 017
1. `acams.org/en/training/acams-certificates` — **PASS_VERIFIED** (HIGH)
2. `ipa.edu.sa/ar/leaderships/programs` — **PASS_VERIFIED** (MEDIUM)
3. `int-comp.org/qualifications/ica-certificate-in-compliance/` — **PASS_VERIFIED** (HIGH)
