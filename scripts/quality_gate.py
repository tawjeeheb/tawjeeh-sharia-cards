"""
بوابة الجودة — فحص آلي لبطاقات مشروع الشريعة
الاستخدام: python scripts/quality_gate.py outputs/test_card_007_katib_adl.md
"""

import sys
import re
import os

# دمج فحوصات العقد C11-C22
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _scripts_dir)
try:
    from validate_card_contract import run_contract_checks
    _CONTRACT_AVAILABLE = True
except ImportError:
    _CONTRACT_AVAILABLE = False

try:
    from scope_guard import run_scope_check
    _SCOPE_GUARD_AVAILABLE = True
except ImportError:
    _SCOPE_GUARD_AVAILABLE = False

ELEMENTS_ORDER = [
    'المسميات المكافئة',
    'التصنيف الوطني SSC',
    'طبيعة العمل',
    'المهام الرئيسية',
    'المرتبة والراتب',
    'المزايا الوظيفية',
    'الشروط والمؤهلات',
    'متطلبات التقييم والتهيئة المهنية',
    'الخبرات المطلوبة',
    'برامج التأهيل المعتمدة',
    'المهارات المطلوبة',
    'الدورات الداعمة',
    'جهات التوظيف وطرق التقديم',
    'المسار الوظيفي والتطور المهني',
    'الشهادات المهنية الاحترافية',
    'الملاحظات المهنية المتقدمة',
    'النصائح العملية الإضافية',
    'جدول مدى قبول التخصصات',
]

ACCEPTANCE_TABLE_HEADERS = ['التخصص', 'مدى القبول', 'السبب', 'ما يرفع القبول']
FORBIDDEN_EXTRA_COL = 'ملاحظات دقيقة'

TAHDEEL_EXCEPTION_ELEMENT = 'برامج التأهيل المعتمدة'


def load(path):
    with open(path, encoding='utf-8') as f:
        return f.readlines(), f.name if hasattr(f, 'name') else path


def run_checks(path):
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    content = ''.join(lines)

    results = []  # (check_id, label, status, detail)
    # status: PASS | FAIL | MANUAL

    # ── C1: عدم وجود `-` كبادئة تعداد ──────────────────────────────────────────
    in_tahdeel = False
    bad_dash_lines = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == TAHDEEL_EXCEPTION_ELEMENT:
            in_tahdeel = True
            continue
        # أي عنوان آخر يوقف استثناء برامج التأهيل
        if stripped in ELEMENTS_ORDER and stripped != TAHDEEL_EXCEPTION_ELEMENT:
            in_tahdeel = False
        # شرطة مقبولة: داخل span HTML (الشروط والمؤهلات) أو داخل سطر برامج التأهيل
        if re.match(r'^\s*-\s+', line):
            if in_tahdeel:
                continue  # الاستثناء الوحيد: داخل سطر برامج التأهيل للفصل بين البرنامج والجهة
            bad_dash_lines.append(i)

    if bad_dash_lines:
        results.append(('C1', 'لا شرطة كبادئة تعداد', 'FAIL',
                         f'سطور: {bad_dash_lines[:5]}'))
    else:
        results.append(('C1', 'لا شرطة كبادئة تعداد', 'PASS', ''))

    # ── C2: لا روابط خام ────────────────────────────────────────────────────────
    raw_urls = []
    for i, line in enumerate(lines, 1):
        # أزل أولًا الروابط المدمجة [نص](url) من السطر قبل الفحص
        clean_line = re.sub(r'\[[^\]]*\]\([^)]*\)', '', line)
        # ابحث عن روابط خام متبقية
        matches = re.finditer(r'https?://[^\s\)\"\'<>]+', clean_line)
        for m in matches:
            raw_urls.append((i, m.group(0)[:60]))
    if raw_urls:
        results.append(('C2', 'لا روابط خام', 'FAIL',
                         f'أمثلة: {raw_urls[:3]}'))
    else:
        results.append(('C2', 'لا روابط خام', 'PASS', ''))

    # ── C3: وجود 18 عنصرًا بالترتيب ────────────────────────────────────────────
    found_elements = []
    for line in lines:
        s = line.strip()
        if s in ELEMENTS_ORDER:
            found_elements.append(s)

    missing = [e for e in ELEMENTS_ORDER if e not in found_elements]
    wrong_order = (found_elements != [e for e in ELEMENTS_ORDER if e in found_elements])

    if missing:
        results.append(('C3', 'وجود 18 عنصرًا', 'FAIL',
                         f'مفقود: {missing}'))
    elif wrong_order:
        results.append(('C3', 'ترتيب العناصر', 'FAIL',
                         f'الترتيب الفعلي: {found_elements}'))
    else:
        results.append(('C3', 'وجود 18 عنصرًا بالترتيب', 'PASS',
                         f'وُجد {len(found_elements)} عنصرًا'))

    # ── C4: عنوان الغلاف خالٍ من القوسين ────────────────────────────────────────
    html_path = path.replace('outputs/', 'outputs/pdf/').replace('.md', '.html')
    # fallback: stem
    if not os.path.exists(html_path):
        stem = os.path.splitext(os.path.basename(path))[0]
        html_path = os.path.join(os.path.dirname(path),
                                 '..', 'outputs', 'pdf', stem + '.html')
        html_path = os.path.normpath(html_path)

    if os.path.exists(html_path):
        with open(html_path, encoding='utf-8') as f:
            html = f.read()
        m = re.search(r'class="profession-title">(.*?)</div>', html)
        if m:
            title = m.group(1)
            if re.search(r'\(|\)', title):
                results.append(('C4', 'عنوان الغلاف خالٍ من القوسين', 'FAIL',
                                 f'العنوان الحالي: {title}'))
            else:
                results.append(('C4', 'عنوان الغلاف خالٍ من القوسين', 'PASS',
                                 f'العنوان: {title}'))
        else:
            results.append(('C4', 'عنوان الغلاف', 'MANUAL',
                             'لم يُعثر على .profession-title في HTML'))
    else:
        results.append(('C4', 'عنوان الغلاف (HTML غير موجود)', 'MANUAL',
                         f'المسار المتوقع: {html_path}'))

    # ── C5: النص بين القوسين موجود حرفيًا في المسميات المكافئة ──────────────────
    title_paren = ''
    for line in lines:
        s = line.strip()
        if re.match(r'^\d+\.\s+', s) and len(s) < 35:
            m = re.search(r'\(([^)]+)\)', s)
            if m:
                title_paren = m.group(1).strip()
            break

    if title_paren:
        # استخراج محتوى "المسميات المكافئة"
        musamma_content = ''
        in_musamma = False
        for line in lines:
            s = line.strip()
            if s == 'المسميات المكافئة':
                in_musamma = True
                continue
            if in_musamma and s in ELEMENTS_ORDER:
                break
            if in_musamma and s:
                musamma_content += s + ' '

        tokens = [t.strip() for t in re.split(r'[،,\s]+', musamma_content) if t.strip()]
        if title_paren in tokens:
            results.append(('C5', f'"{title_paren}" موجود حرفيًا في المسميات المكافئة',
                             'PASS', f'المسميات: {musamma_content.strip()}'))
        else:
            results.append(('C5', f'"{title_paren}" موجود حرفيًا في المسميات المكافئة',
                             'FAIL',
                             f'النص المطلوب: "{title_paren}" — المسميات الحالية: "{musamma_content.strip()}"'))
    else:
        results.append(('C5', 'لا يوجد نص بين قوسين في H1', 'PASS', 'لا شيء يلزم نقله'))

    # ── C6: جدول القبول — 4 أعمدة فقط لا خامس ──────────────────────────────────
    table_lines = [l for l in lines if '|' in l]
    extra_col_found = any(FORBIDDEN_EXTRA_COL in l for l in table_lines)
    if extra_col_found:
        results.append(('C6', 'جدول القبول: لا عمود خامس', 'FAIL',
                         f'وُجد عمود "{FORBIDDEN_EXTRA_COL}"'))
    else:
        # تحقق من أن رأس الجدول يحتوي الأعمدة الأربعة
        header_ok = False
        for l in table_lines:
            if all(h in l for h in ACCEPTANCE_TABLE_HEADERS):
                header_ok = True
                break
        if header_ok:
            results.append(('C6', 'جدول القبول: 4 أعمدة صحيحة', 'PASS', ''))
        else:
            results.append(('C6', 'جدول القبول: رأس الجدول', 'MANUAL',
                             'لم يُعثر على الأعمدة الأربعة — تحقق يدويًا'))

    # ── C7: تحذير تشابه العناصر الحساسة بين البطاقات ────────────────────────────
    SENSITIVE_ELEMENTS = [
        'المهارات المطلوبة',
        'الدورات الداعمة',
        'برامج التأهيل المعتمدة',
        'الشهادات المهنية الاحترافية',
        'الملاحظات المهنية المتقدمة',
        'النصائح العملية الإضافية',
    ]
    SIMILARITY_THRESHOLD = 0.60

    def extract_links_and_names(card_lines, element_name):
        """استخرج الروابط والأسماء من عنصر معين."""
        in_element = False
        tokens = set()
        for line in card_lines:
            s = line.strip()
            if s == element_name:
                in_element = True
                continue
            if in_element and s in ELEMENTS_ORDER:
                break
            if in_element and s:
                # استخرج نصوص الروابط [نص](url) والروابط نفسها
                for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
                    tokens.add(m.group(1).strip())
                    tokens.add(m.group(2).strip())
        return tokens

    def jaccard_similarity(set_a, set_b):
        if not set_a and not set_b:
            return 0.0
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union) if union else 0.0

    outputs_dir = os.path.dirname(path)
    other_cards = [
        f for f in os.listdir(outputs_dir)
        if f.endswith('.md') and os.path.join(outputs_dir, f) != path
    ]

    c7_warnings = []
    for other_name in sorted(other_cards):
        other_path = os.path.join(outputs_dir, other_name)
        try:
            with open(other_path, encoding='utf-8') as f:
                other_lines = f.readlines()
        except Exception:
            continue
        for elem in SENSITIVE_ELEMENTS:
            tokens_current = extract_links_and_names(lines, elem)
            tokens_other = extract_links_and_names(other_lines, elem)
            if not tokens_current or not tokens_other:
                continue
            sim = jaccard_similarity(tokens_current, tokens_other)
            if sim >= SIMILARITY_THRESHOLD:
                c7_warnings.append(
                    f'{elem} ↔ {other_name}: {int(sim * 100)}% تشابه'
                )

    if c7_warnings:
        detail = ' | '.join(c7_warnings[:5])
        results.append(('C7', 'تشابه العناصر الحساسة بين البطاقات', 'MANUAL',
                         f'⚠️ يُمنع الاعتماد حتى يُكتب تبرير مهني: {detail}'))
    else:
        results.append(('C7', 'لا تشابه ≥60% في العناصر الحساسة مع بطاقات أخرى', 'PASS', ''))

    # ── C8: وجود ملف evidence لدعم الشهادات المهنية ────────────────────────────
    has_certs_element = 'الشهادات المهنية الاحترافية' in content
    if has_certs_element:
        stem = os.path.splitext(os.path.basename(path))[0]
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
        evidence_path = os.path.join(repo_root, 'outputs', 'evidence',
                                     f'{stem}_certifications_support_audit.md')
        if os.path.exists(evidence_path):
            results.append(('C8', 'ملف تحقق دعم الشهادات موجود', 'PASS',
                             f'→ {os.path.relpath(evidence_path, repo_root)}'))
        else:
            results.append(('C8', 'ملف تحقق دعم الشهادات مفقود', 'MANUAL',
                             f'⚠️ يجب إنشاء: outputs/evidence/{stem}_certifications_support_audit.md'))
    else:
        results.append(('C8', 'لا يوجد عنصر شهادات — C8 غير مطبّق', 'PASS', ''))

    # ── C9: لا عناوين قطاعية داخل "الشروط والمؤهلات" ───────────────────────────
    CONDS_ELEMENT = 'الشروط والمؤهلات'
    NEXT_AFTER_CONDS = 'متطلبات التقييم والتهيئة المهنية'
    in_conds = False
    sector_in_conds = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == CONDS_ELEMENT:
            in_conds = True
            continue
        if in_conds and stripped == NEXT_AFTER_CONDS:
            break
        if in_conds and re.search(r'class="sector-label"', line):
            sector_in_conds.append(i)
    if sector_in_conds:
        results.append(('C9', 'عناوين قطاعية في الشروط والمؤهلات', 'MANUAL',
                         f'⚠️ سطور {sector_in_conds[:5]} — مسموح فقط لبطاقات متعددة القطاعات الحقيقية (حكومي+مرخص). تحقق بشري مطلوب.'))
    else:
        results.append(('C9', 'لا عناوين قطاعية في الشروط والمؤهلات', 'PASS', ''))

    # ── C10: عنوان البطاقة غير فارغ في HTML ────────────────────────────────────
    if os.path.exists(html_path):
        with open(html_path, encoding='utf-8') as f:
            html_c10 = f.read()
        m10 = re.search(r'class="profession-title">(.*?)</div>', html_c10)
        if m10:
            title_c10 = m10.group(1).strip()
            if title_c10:
                results.append(('C10', 'عنوان البطاقة غير فارغ في HTML', 'PASS',
                                 f'العنوان: {title_c10}'))
            else:
                results.append(('C10', 'عنوان البطاقة فارغ في HTML', 'FAIL',
                                 '❌ profession-title فارغ — العنوان لن يظهر في PDF'))
        else:
            results.append(('C10', 'عنوان البطاقة غير موجود في HTML', 'FAIL',
                             '❌ لم يُعثر على div.profession-title في HTML'))
    else:
        results.append(('C10', 'عنوان البطاقة (HTML غير موجود)', 'MANUAL',
                         f'المسار المتوقع: {html_path}'))

    # ── C11-C22: فحوصات العقد ────────────────────────────────────────────────────
    if _CONTRACT_AVAILABLE:
        contract_results = run_contract_checks(path)
        for cr in contract_results:
            results.append((cr[0], cr[1], cr[2], cr[3]))
    else:
        results.append(('C11+', 'فحوصات العقد (C11-C22)', 'MANUAL',
                         '⚠️ validate_card_contract.py غير موجود — تحقق يدوي مطلوب'))

    # ── C23: Scope Guard ────────────────────────────────────────────────────────
    if _SCOPE_GUARD_AVAILABLE:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
        stem = os.path.splitext(os.path.basename(path))[0]
        lock_path = os.path.join(repo_root, 'outputs', 'locks', f'{stem}_scope_lock.json')
        scope_results = run_scope_check(path, lock_path, allowed_elements=None)
        for sr in scope_results:
            results.append((sr[0], sr[1], sr[2], sr[3]))
    else:
        results.append(('C23', 'Scope Guard (غير متاح)', 'MANUAL', '⚠️ scope_guard.py غير موجود'))

    return results, title_paren


def print_report(results, title_paren, path):
    total = len(results)
    passed = sum(1 for r in results if r[2] == 'PASS')
    failed = sum(1 for r in results if r[2] == 'FAIL')
    manual = sum(1 for r in results if r[2] == 'MANUAL')

    overall = 'PASS' if failed == 0 else 'FAIL'

    print('=' * 60)
    print(f'  بوابة الجودة — {os.path.basename(path)}')
    print('=' * 60)
    for r in results:
        icon = {'PASS': '✅', 'FAIL': '❌', 'MANUAL': '⚠️ '}[r[2]]
        print(f'  {icon} [{r[0]}] {r[1]}')
        if r[3]:
            print(f'       → {r[3]}')
    print('-' * 60)
    print(f'  النتيجة: {overall}  |  ✅ {passed}  ❌ {failed}  ⚠️  {manual}  من {total}')
    print('=' * 60)
    return overall, passed, failed, manual


def build_md_report(results, title_paren, path, overall, passed, failed, manual):
    stem = os.path.splitext(os.path.basename(path))[0]
    lines = []
    lines.append(f'# تقرير الجودة — {stem}\n')
    lines.append(f'\n**النتيجة الكلية:** {"PASS ✅" if overall == "PASS" else "FAIL ❌"}\n')
    lines.append(f'**الملف المفحوص:** `{path}`\n')
    lines.append(f'**تاريخ الفحص:** مُولَّد آليًا\n\n')
    lines.append('---\n\n')
    lines.append('## نتائج الفحوصات الآلية\n\n')
    lines.append('| الكود | الفحص | النتيجة | التفاصيل |\n')
    lines.append('|-------|-------|---------|----------|\n')
    for r in results:
        icon = {'PASS': '✅ PASS', 'FAIL': '❌ FAIL', 'MANUAL': '⚠️ MANUAL'}[r[2]]
        lines.append(f'| {r[0]} | {r[1]} | {icon} | {r[3]} |\n')
    lines.append('\n---\n\n')
    lines.append('## ملخص\n\n')
    lines.append(f'- فحوصات ناجحة: {passed}\n')
    lines.append(f'- فحوصات فاشلة: {failed}\n')
    lines.append(f'- تتطلب مراجعة يدوية: {manual}\n\n')
    lines.append('## بنود المراجعة اليدوية المطلوبة\n\n')
    lines.append('راجع `prompts/QUALITY_GATE_ELEMENT_AUDIT.md` للبنود التالية:\n\n')
    lines.append('- [ ] MR-01: دقة محتوى المسميات المكافئة\n')
    lines.append('- [ ] MR-02: دقة جدول القبول (السند الرسمي لكل مستوى)\n')
    lines.append('- [ ] MR-03: دقة الروابط (رسمية حقيقية، لا مخترعة)\n')
    lines.append('- [ ] MR-04: دقة الملاحظات المهنية المتقدمة\n')
    lines.append('- [ ] MR-05: قفل نطاق العنصر (إن كان هناك تعديل جزئي)\n')
    lines.append('- [ ] MR-06: الشروط والمؤهلات مستندة إلى مصدر رسمي\n')
    return ''.join(lines)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('الاستخدام: python scripts/quality_gate.py <مسار_البطاقة>')
        sys.exit(1)

    card_path = os.path.abspath(sys.argv[1])
    if not os.path.exists(card_path):
        print(f'خطأ: الملف غير موجود: {card_path}')
        sys.exit(1)

    results, title_paren = run_checks(card_path)
    overall, passed, failed, manual = print_report(results, title_paren, card_path)

    # اكتب تقرير MD إذا طُلب أو تلقائيًا
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(repo_root, 'outputs', 'quality_reports')
    os.makedirs(reports_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(card_path))[0]
    report_path = os.path.join(reports_dir, f'{stem}_quality_report.md')
    report_md = build_md_report(results, title_paren, card_path, overall, passed, failed, manual)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_md)
    print(f'\n  تقرير MD: {report_path}')

    sys.exit(0 if overall == 'PASS' else 1)
