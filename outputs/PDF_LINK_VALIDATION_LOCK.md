# PDF LINK VALIDATION LOCK v1.0
## قفل التحقق من روابط PDF — نظام إلزامي دائم

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

---

## القاعدة الصارمة

```
FAIL_OPEN > 0  →  فشل إلزامي — لا اعتماد — لا commit
```

لا توجد استثناءات. لا مراجعة يدوية. النظام هو المسؤول الكامل.

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
