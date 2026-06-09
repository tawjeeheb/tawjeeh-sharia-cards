Tawjeeh Sharia Cards Project

## قبل توليد أي بطاقة

```bash
# 1. فحص الروابط أولًا
python3 outputs/check_links.py outputs/test_card_XXX.md

# 2. توليد PDF بعد اجتياز الفحص
python3 outputs/pdf/convert.py
```

## الملفات الحاكمة

| الملف | الغرض |
|-------|-------|
| `outputs/VISUAL_CLEAN_PAGE_LOCK.md` | قفل النظافة البصرية + منطق القوائم الذكي (commit `323493c`) |
| `outputs/LINK_POLICY.md` | سياسة الروابط المعتمدة لجميع البطاقات |
| `outputs/check_links.py` | سكربت فحص الروابط قبل التوليد |
| `outputs/pdf/convert.py` | قالب التوليد (CSS + شكل الروابط مقفول) |
| `outputs/test_card_001_qadi.md` | البطاقة المرجعية النموذج |
| `outputs/READER_FIRST_COURSE_TITLE_LOCK.md` | قفل تسمية الدورات بصيغة قارئية وظيفية عربية |
| `outputs/LINK_VALIDATION_LOCK.md` | قفل دائم لجميع الروابط الخارجية — شروط القبول الإلزامية |
| `outputs/COURSERA_LINK_LOCK.md` | قفل دائم لروابط Coursera — شروط القبول الإلزامية |
| `outputs/link_audit_qadi_v1.md` | ملف تدقيق روابط بطاقة قاضي |
| `outputs/ROLE_SPECIFIC_CONTENT_LOCK.md` | قفل حاكم — كل بطاقة تُبنى من الصفر؛ 18 عنصرًا واجب التخصيص؛ اختبار القبول الستة |
| `outputs/CONTENT_DECISION_ENGINE.md` | محرك قرار المحتوى — 9 خطوات إلزامية؛ بطاقة قاضي = Golden Master للتصميم فقط لا للمحتوى |
| `outputs/COURSE_SELECTION_ENGINE.md` | محرك اختيار الدورات — الاختيار يبدأ من المهارة؛ 3 مراحل + اختبار عدم النسخ + اختبار القبول |
| `outputs/CERTIFICATION_SELECTION_ENGINE.md` | محرك اختيار الشهادات — 10 مسارات مهنية؛ يبدأ من المهمة الحرجة لا من الشهرة؛ اختبار القبول |
