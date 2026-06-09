#!/usr/bin/env python3
"""
check_links.py — فحص الروابط قبل توليد أي بطاقة مهنية
الاستخدام:
  python3 outputs/check_links.py outputs/test_card_XXX.md
  python3 outputs/check_links.py outputs/test_card_XXX.md --final
"""

import re
import sys
from urllib.parse import urlparse, parse_qs

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

def evaluate_link(text: str, url: str, final: bool = False):
    issues = []
    blocked = []

    for pattern, label in WEAK_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            issues.append(label)

    if is_likely_homepage(url) and 'صفحة رئيسية' not in ' '.join(issues):
        issues.append("يبدو صفحة رئيسية أو قائمة عامة — مسار قصير جدًا")

    if final:
        parsed = urlparse(url)
        if parsed.query:
            blocked.append(f"BLOCKED_QUERY_PARAMS: يحتوي على query parameters ({parsed.query[:60]})")

    return issues, blocked

# ─── التقرير الرئيسي ──────────────────────────────────────────────────────────

def run(md_path: str, final: bool = False):
    with open(md_path, encoding='utf-8') as f:
        content = f.read()

    links = extract_links(content)

    if not links:
        print("✓ لا توجد روابط في الملف.")
        return

    total = len(links)
    clean = 0
    flagged = []
    hard_blocked = []

    mode_label = "وضع --final (LINK_VALIDATION_LOCK)" if final else "الفحص الأساسي"
    print(f"\n{'='*70}")
    print(f"  فحص الروابط: {md_path}")
    print(f"  الوضع: {mode_label}")
    print(f"{'='*70}")
    print(f"  إجمالي الروابط: {total}\n")

    for text, url in links:
        issues, blocked = evaluate_link(text, url, final=final)
        if blocked:
            hard_blocked.append((text, url, blocked))
        elif issues:
            flagged.append((text, url, issues))
        else:
            clean += 1

    # ─── النتائج ──────────────────────────────────────────────────────────────
    print(f"  ✅ مقبول: {clean}")
    print(f"  ⚠️  يحتاج مراجعة: {len(flagged)}")
    if final:
        print(f"  ❌ BLOCKED (رفض نهائي): {len(hard_blocked)}")
    print()

    if hard_blocked:
        print("─" * 70)
        print("  ❌ BLOCKED — روابط مرفوضة نهائيًا (--final):")
        print("─" * 70)
        for text, url, blocked in hard_blocked:
            print(f"\n  النص   : {text[:60]}")
            print(f"  الرابط : {url[:80]}")
            for b in blocked:
                print(f"  ❌  {b}")

    if flagged:
        print("─" * 70)
        print("  ⚠️  الروابط التي تحتاج مراجعة:")
        print("─" * 70)
        for text, url, issues in flagged:
            print(f"\n  النص   : {text[:60]}")
            print(f"  الرابط : {url[:80]}")
            for issue in issues:
                print(f"  ⚠️   {issue}")

    print()
    print("─" * 70)
    if final:
        print("  وضع --final: يرفض أي رابط يحتوي على query parameters.")
        if hard_blocked:
            print("  ❌ الملف لا يجتاز LINK_VALIDATION_LOCK — يجب إصلاح الروابط المرفوضة.")
        else:
            print("  ✅ الملف اجتاز LINK_VALIDATION_LOCK — لا توجد روابط مرفوضة نهائيًا.")
    else:
        print("  تذكير: هذا الفحص يكتشف الأنماط الضعيفة الواضحة فقط.")
        print("  التحقق الفعلي من صحة الرابط يتطلب فتحه يدويًا خارج بيئة التشغيل.")
    print("─" * 70)

    if hard_blocked:
        sys.exit(2)  # BLOCKED
    elif flagged:
        sys.exit(1)  # يحتاج مراجعة

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print("الاستخدام: python3 check_links.py <مسار_ملف_md> [--final]")
        sys.exit(1)
    md_path = args[0]
    final_mode = '--final' in args
    run(md_path, final=final_mode)
