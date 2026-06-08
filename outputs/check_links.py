#!/usr/bin/env python3
"""
check_links.py — فحص الروابط قبل توليد أي بطاقة مهنية
الاستخدام: python3 outputs/check_links.py outputs/test_card_XXX.md
"""

import re
import sys
from urllib.parse import urlparse

# ─── أنماط الروابط الضعيفة أو الممنوعة ──────────────────────────────────────

WEAK_PATTERNS = [
    # صفحات رئيسية (مسار فارغ أو "/" فقط)
    (r'^/$', "صفحة رئيسية — المسار فارغ"),
    (r'^/\s*$', "صفحة رئيسية — المسار فارغ"),

    # صفحات بحث
    (r'[?&](q|query|search|s)=', "رابط بحث"),
    (r'/search[/?]', "رابط بحث"),

    # روابط مختصرة من طرف ثالث
    (r'^https?://(bit\.ly|goo\.gl|tinyurl\.com|t\.co|ow\.ly|rb\.gy)/', "رابط مختصر من طرف ثالث"),

    # صفحات عامة مشتبه بها
    (r'/news/', "صفحة أخبار — تحقق إذا كانت بديلًا عن صفحة التسجيل"),
    (r'/blog/', "صفحة مدونة — تحقق إذا كانت بديلًا عن صفحة البرنامج"),
    (r'/tag/', "صفحة وسم/تصنيف — عامة"),
    (r'/category/', "صفحة تصنيف — عامة"),

    # ويكيبيديا ومصادر غير رسمية
    (r'wikipedia\.org', "ويكيبيديا — غير رسمي"),
    (r'youtube\.com', "YouTube — تحقق إذا كانت قناة رسمية أم لا"),

    # روابط PDF عامة (قد تكون مقبولة لكن تحتاج مراجعة)
    (r'\.pdf$', "رابط PDF — تأكد أنه الوثيقة الرسمية للبرنامج/الشهادة"),
]

# أنماط الصفحات الرئيسية بمسار قصير جدًا (أقل من مقطعين)
def is_likely_homepage(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.rstrip('/')
    # مسار فارغ أو مقطع واحد فقط وقصير جدًا
    parts = [p for p in path.split('/') if p]
    if len(parts) == 0:
        return True
    if len(parts) == 1 and len(parts[0]) < 4:
        return True
    return False

# ─── استخراج الروابط من Markdown ─────────────────────────────────────────────

def extract_links(text: str):
    """استخراج جميع الروابط من صيغة Markdown [نص](رابط)"""
    return re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)

# ─── تقييم رابط واحد ──────────────────────────────────────────────────────────

def evaluate_link(text: str, url: str):
    issues = []

    for pattern, label in WEAK_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            issues.append(label)

    if is_likely_homepage(url) and 'صفحة رئيسية' not in ' '.join(issues):
        issues.append("يبدو صفحة رئيسية أو قائمة عامة — مسار قصير جدًا")

    return issues

# ─── التقرير الرئيسي ──────────────────────────────────────────────────────────

def run(md_path: str):
    with open(md_path, encoding='utf-8') as f:
        content = f.read()

    links = extract_links(content)

    if not links:
        print("✓ لا توجد روابط في الملف.")
        return

    total = len(links)
    clean = 0
    flagged = []

    print(f"\n{'='*70}")
    print(f"  فحص الروابط: {md_path}")
    print(f"{'='*70}")
    print(f"  إجمالي الروابط: {total}\n")

    for text, url in links:
        issues = evaluate_link(text, url)
        if issues:
            flagged.append((text, url, issues))
        else:
            clean += 1

    # ─── النتائج النظيفة ──────────────────────────────────────────────────────
    print(f"  ✅ مقبول ظاهريًا: {clean}")
    print(f"  ⚠️  يحتاج مراجعة: {len(flagged)}")
    print()

    if flagged:
        print("─" * 70)
        print("  الروابط التي تحتاج مراجعة:")
        print("─" * 70)
        for text, url, issues in flagged:
            print(f"\n  النص   : {text[:60]}")
            print(f"  الرابط : {url[:80]}")
            for issue in issues:
                print(f"  ⚠️   {issue}")

    print()
    print("─" * 70)
    print("  تذكير: هذا الفحص يكتشف الأنماط الضعيفة الواضحة فقط.")
    print("  التحقق الفعلي من صحة الرابط يتطلب فتحه يدويًا خارج بيئة التشغيل.")
    print("─" * 70)

    if flagged:
        sys.exit(1)  # exit code غير صفري لتسهيل التكامل مع CI

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("الاستخدام: python3 check_links.py <مسار_ملف_md>")
        sys.exit(1)
    run(sys.argv[1])
