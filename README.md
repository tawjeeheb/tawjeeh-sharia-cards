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
| `outputs/LINK_VALIDATION_LOCK.md` | قفل دائم لجميع الروابط الخارجية — شروط القبول الإلزامية |
| `outputs/COURSERA_LINK_LOCK.md` | قفل دائم لروابط Coursera — شروط القبول الإلزامية |
| `outputs/link_audit_qadi_v1.md` | ملف تدقيق روابط بطاقة قاضي |
