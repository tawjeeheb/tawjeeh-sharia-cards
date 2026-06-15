# PDF LINK VALIDATION LOCK v1.2
## قفل التحقق من روابط PDF — نظام إلزامي دائم
## + LINK SELECTION & VERIFICATION PROTOCOL v1.0

---

## LINK SELECTION & VERIFICATION PROTOCOL v2.0 — الطبقة الأولى (قبل الإدراج)
## + SMART LINK RESOLUTION ENGINE v1.0

**القاعدة المطلقة:** المستخدم لا يراجع الروابط يدويًا. النظام لا يدرج أي رابط حرج إلا إذا كان HIGH_VERIFIED.

```
السجل ليس whitelist مغلقًا؛ السجل Cache ذكي.
أي رابط جديد يُحلَّل تلقائيًا عبر SMART LINK RESOLUTION ENGINE
ويُرقَّى إلى HIGH_VERIFIED أو يُستبدَل — دون تدخل المستخدم.

الرابط الصحيح في النوع الخطأ = رابط مرفوض.
HIGH_VERIFIED وحده لا يكفي — يجب أن يتطابق نوع الرابط مع نوع القسم.
```

### LINK TYPE BOUNDARY LOCK v1.0 — الطبقة الثانية (بعد HIGH_VERIFIED)

| القسم | الأنواع المقبولة | مثال مرفوض |
|---|---|---|
| برامج التأهيل المعتمدة | `program`, `diploma`, `degree` | SHRM-CP (certification) في برامج التأهيل |
| الشهادات المهنية الاحترافية | `certification` | ICA Program (program) في الشهادات |
| الدورات الداعمة | `course` من منصة معتمدة | edX (منصة غير معتمدة) |

**أخطاء القفل:**
- `TYPE_MISMATCH` — نوع الرابط لا يطابق القسم
- `COURSE_PLATFORM_NOT_ALLOWED` — منصة الدورة غير معتمدة
- `DUPLICATE_ENTITY_ACROSS_SECTIONS` — نفس الرابط في أكثر من قسم
- `UNKNOWN_TYPE` — حقل type مفقود في السجل

**موقع التطبيق:** Step 1.5 في `run_card_pipeline.py` — بعد SMART LINK RESOLUTION وقبل توليد PDF.

### الأقسام الحرجة (تطبّق عليها القاعدة بالكامل):
- برامج التأهيل المعتمدة
- الشهادات المهنية الاحترافية
- الدورات الداعمة

### الممنوعات:
```
ممنوع إدراج رابط حرج بدرجة MEDIUM أو UNKNOWN أو NOT_VERIFIED أو NEEDS_RESOLUTION.
ممنوع تخمين URL من نمط متوقع دون دليل WebSearch مؤكد.
ممنوع استخدام صفحة رئيسية عامة أو صفحة كلية أو صفحة منصة عامة.
ممنوع استخدام رابط يتطلب تسجيل دخول.
إذا الرابط غير موجود في السجل → يشغّل SMART LINK RESOLUTION ENGINE تلقائيًا.
إذا فشل الاكتشاف → استبدل المحتوى ببديل يملك رابطًا HIGH_VERIFIED.
```

### مسار حل الرابط التلقائي:
```
رابط جديد في البطاقة
    ↓
هل هو في السجل؟
    ├─ HIGH_VERIFIED → ✅ قبول مباشر (CACHE_HIT_HIGH)
    ├─ REJECTED / NOT_VERIFIED → ❌ استبدال إلزامي (CACHE_HIT_BAD)
    └─ UNKNOWN / غير موجود
         ↓
         SMART LINK RESOLUTION ENGINE
         [WebSearch للاكتشاف التلقائي]
              ↓
         هل الصفحة محددة + هل الاسم ظاهر في النتيجة؟
              ├─ نعم → DISCOVERED → أُضيف للسجل HIGH_VERIFIED → ✅
              └─ لا  → ابحث عن بديل HIGH_VERIFIED → استبدل → ✅
```

### آلية التطبيق:
- **Step 1** في `run_card_pipeline.py` — `step_resolve_links()` يحل كل رابط حرج تلقائيًا.
- `scripts/check_critical_links.py` — سكريبت مستقل للفحص (يُعيد NEEDS_RESOLUTION للمجهول).
- `scripts/smart_link_resolver.py` — محرك الاكتشاف والتحقق التلقائي.
- `references/verified_link_registry.json` — السجل الآلي (machine-readable Cache).
- `references/verified_link_registry.md` — السجل البشري القابل للقراءة.

---

## المشكلة التي يحلّها هذا القفل

روابط Markdown والـ HTML ليست ضمانة أن رابط PDF annotation صحيح.
أسباب التفاوت الممكنة:
- محارف Unicode خفية في href (invisible zero-width chars).
- علامات ترقيم trailing داخل href (نقطة، فاصلة، سهم ↗).
- تحويلات خاطئة أثناء markdown → HTML → PDF.

لهذا، **الفحص يكون من ملف PDF نفسه — لا من Markdown ولا من HTML.**

---

## التعريفات

| الحالة | المعنى |
|--------|---------|
| **PASS_OPEN** | HTTP ≠ 000 — الخادم يستجيب (حتى 403 بسبب IP يُعدّ PASS) |
| **FAIL_OPEN** | HTTP = 000 — النطاق غير موجود أو لا استجابة إطلاقًا |
| **REPLACED_OPEN** | كان FAIL_OPEN وتم استبداله تلقائيًا (للتقارير فقط) |

### وضع USER_OPEN_STRICT (الافتراضي في pipeline)

| الحالة | المعنى |
|--------|---------|
| **PASS_OFFICIAL_SPECIFIC** | الخادم يستجيب وليس login-required ولا bare homepage (بما في ذلك 403) |
| **FAIL_USER_OPEN** | HTTP = 000 أو 404 أو URL يطابق KNOWN_LOGIN_REQUIRED |
| **WARN_GENERAL_PAGE** | URL صفحة رئيسية بلا مسار محدد (مقبول لأقسام التوظيف) |

**KNOWN_LOGIN_REQUIRED** (تستلزم تسجيل دخول — لا يمكن للقارئ فتحها):
- `lms.doroob.sa/courses/` — منصة درّوب (تتطلب حساب حكومي)
- `fa.gov.sa/Services/ProgramDetails/` — الأكاديمية المالية (خدمات محمية)

---

## القاعدة الصارمة

```
FAIL_OPEN > 0  →  فشل إلزامي — لا اعتماد — لا commit
FAIL_USER_OPEN > 0  →  فشل إلزامي — لا اعتماد — لا commit
```

لا يتحمل المستخدم مراجعة الروابط يدويًا. النظام مسؤول عن فحص روابط PDF النهائية واستبدال أي رابط غير صالح أو غير نافع للقارئ.

لا توجد استثناءات. لا مراجعة يدوية. النظام هو المسؤول الكامل.

---

## قاعدة تنوع منصات الدورات

الدورات الداعمة يجب أن تكون متنوعة المصدر. النمط المفضّل:
- 3 دورات Coursera (بمزودين مختلفين على الأقل)
- 2 دورات إثرائي/إيثراEd

**محظور:** دورات all-doroob (جميعها من منصة درّوب) — الروابط المحمية تفشل FAIL_USER_OPEN.

**مسموح:** Coursera + إثرائي + ACAMS + CFA Institute عبر Coursera. روابط fa.gov.sa العامة (الصفحة الرئيسية فقط) = WARN_GENERAL_PAGE (مقبول للتوظيف لا للدورات).

---

## روابط الفوتر المستثناة (مفحوصة ومعتمدة مسبقًا)

```
https://www.tiktok.com/@tawjeeh.hub
https://instagram.com/tawjeeh.hub
https://www.snapchat.com/add/tawjeeh.hub
https://x.com/tawjeeh_hub
https://www.youtube.com/@tawjeeh_hub
https://www.tawjeeh.hub
```

---

## مكونات النظام

### 1. `scripts/validate_pdf_links.py`
سكريبت مستقل. يُنفَّذ على أي ملف PDF:
```bash
python scripts/validate_pdf_links.py outputs/pdf/test_card_015_*.pdf
python scripts/validate_pdf_links.py --verbose outputs/pdf/tawjeeh_cards_015_017_combined.pdf
```
يخرج بـ exit code 1 إذا FAIL_OPEN > 0.

### 2. `step_pdf_links()` في `scripts/run_card_pipeline.py`
خطوة 5 في pipeline الإنتاج. تُوقف pipeline فورًا إذا FAIL_OPEN > 0.

### 3. `sanitize_url_for_pdf()` في `outputs/pdf/convert.py`
تنظيف تلقائي لكل href قبل توليد PDF:
- يحذف 15 نوعًا من محارف Unicode الخفية.
- يحذف علامات trailing (نقطة، فاصلة، سهم ↗، إلخ).

---

## نتيجة الفحص الاسترجاعي — بطاقات 015/016/017

**تاريخ الفحص:** 2026-06-15

| البطاقة | الروابط الكلية | PASS_OPEN | FAIL_OPEN |
|---------|---------------|-----------|-----------|
| test_card_015_akhsaiy_shuun_amal.pdf | — | — | 0 |
| test_card_016_akhsaiy_himayat_almustathmir.pdf | — | — | 0 |
| test_card_017_akhsaiy_imtithal_mali.pdf | — | — | 0 |
| tawjeeh_cards_015_017_combined.pdf | — | — | 0 |
| **المجموع (dedup)** | **87** | **87** | **0** |

**النتيجة: PASS — جميع الروابط صالحة. FAIL_OPEN = 0.**

---

## ضمان عدم نجاح أي PDF مستقبلي بـ FAIL_OPEN

الضمانات متعددة الطبقات:

1. **`sanitize_url_for_pdf()`** — يمنع دخول روابط فاسدة إلى PDF أصلًا.
2. **`validate_pdf_links.py`** — يفحص كل رابط بعد التوليد.
3. **`step_pdf_links()` في pipeline** — يوقف pipeline ويمنع commit إذا FAIL_OPEN > 0.

أي PDF بـ FAIL_OPEN > 0 **يفشل تلقائيًا** ويظهر في تقرير pipeline قبل أي commit.

## CONTENT PRESERVATION DURING LINK REPAIR LOCK v1.0

إصلاح الرابط لا يسمح بتغيير نوع العنصر أو وظيفة المحتوى.

القاعدة:
* أي تغيير في محتوى البطاقة بسبب الرابط يجب أن يبقى داخل نفس النوع ونفس العنصر.
* برنامج تأهيل ← يُستبدل ببرنامج تأهيل فقط
* شهادة مهنية ← تُستبدل بشهادة مهنية فقط
* دورة ← تُستبدل بدورة من منصة معتمدة فقط
* إذا لم يجد النظام رابطًا مطابقًا لنفس النوع → يوقف الإنتاج ويبلغ عن الفشل
* ممنوع استبدال برنامج بشهادة أو شهادة بدورة أو أي خلط مشابه
* CONTENT_TYPE_VIOLATION → FAIL (أعلى من HIGH_VERIFIED)
