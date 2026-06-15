#!/usr/bin/env python3
"""
CONTENT STRUCTURE FREEZE CHECK v1.0
=====================================
يضمن أن كل بطاقة جديدة تلتزم بالبنية المجمّدة للعناصر الـ 18.

القفول المُطبَّقة:
  ELEMENT SHAPE LOCK             — شكل كل عنصر ثابت بين البطاقات
  CONTENT CROSS-CONTAMINATION LOCK — محتوى عنصر لا يدخل عنصرًا آخر
  FAIL_STRUCTURE_DRIFT           — انحراف بنيوي يتجاوز 15%

الاستخدام:
  python scripts/check_structure_freeze.py data/test_card_018_*.md
  python scripts/check_structure_freeze.py --verbose data/test_card_018_*.md
"""

import argparse
import re
import sys
from pathlib import Path

# ── ترتيب العناصر المجمَّد (18 عنصرًا) ──────────────────────────────────────

FROZEN_ELEMENTS: list[str] = [
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

FROZEN_ELEMENTS_SET = set(FROZEN_ELEMENTS)
TOTAL_ELEMENTS = len(FROZEN_ELEMENTS)  # 18

# ── أعداد ثابتة لكل عنصر ───────────────────────────────────────────────────

REQUIRED_COURSES = 5
REQUIRED_CERTS   = 4  # 4 شهادات بالضبط — لا أقل ولا أكثر
TABLE_COLUMNS    = 4  # أعمدة جدول مدى القبول

# ── قواعد التلوث المتقاطع (CONTENT CROSS-CONTAMINATION LOCK) ───────────────

# أنماط يجب ألا تظهر في العنصر المعطى
CROSS_CONTAMINATION_RULES: list[tuple[str, str, str]] = [
    # (عنصر_يُفحص, نمط_regex_محظور, وصف_الانتهاك)
    (
        'الشروط والمؤهلات',
        r'<span class="condition-label">(قبل التعيين|بعد التعيين)',
        'محتوى "قبل التعيين/بعد التعيين" يخص متطلبات التقييم لا الشروط',
    ),
    (
        'متطلبات التقييم والتهيئة المهنية',
        r'يُشترط.*تخصص|درجة.*البكالوريوس|مؤهل.*علمي',
        'متطلبات أكاديمية أو تخصصية تخص الشروط والمؤهلات — لا متطلبات التقييم',
    ),
    (
        'برامج التأهيل المعتمدة',
        r'shrm\.org/credentials|cipd\.org/en/qualifications|pmi\.org/certifications|cfainstitute\.org|acams\.org/en/certifications|compliancecertification\.org|acfe\.com/cfe',
        'CROSS_CONTAMINATION: شهادة مهنية داخل برامج التأهيل — يخص قسم الشهادات فقط',
    ),
    (
        'الشهادات المهنية الاحترافية',
        r'int-comp\.org/qualifications/ica-certificate|acams\.org/en/training/acams-certificates|garp\.org/frm/program-exams',
        'CROSS_CONTAMINATION: برنامج تأهيل داخل الشهادات — يخص قسم برامج التأهيل فقط',
    ),
    (
        'الدورات الداعمة',
        r'shrm\.org|cipd\.org|pmi\.org/certifications|cfainstitute\.org|acams\.org/en/certifications|compliancecertification\.org|acfe\.com/cfe|int-comp\.org|garp\.org/frm',
        'CROSS_CONTAMINATION: شهادة أو برنامج داخل الدورات الداعمة',
    ),
]

# ── استخراج العناصر من الملف ─────────────────────────────────────────────────

def extract_elements_order(lines: list[str]) -> list[str]:
    """يستخرج العناصر بالترتيب كما ظهرت في الملف."""
    found = []
    for line in lines:
        s = line.strip()
        if s in FROZEN_ELEMENTS_SET:
            found.append(s)
    return found


def extract_section(lines: list[str], element_name: str) -> list[tuple[int, str]]:
    """يستخرج سطور قسم معين."""
    in_section = False
    result = []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s == element_name:
            in_section = True
            continue
        if in_section:
            if s in FROZEN_ELEMENTS_SET:
                break
            result.append((i, line))
    return result


# ── الفحوص ───────────────────────────────────────────────────────────────────

def fsf_c1_all_elements_present(found: list[str]) -> tuple:
    """FSF-C1: جميع العناصر الـ 18 موجودة."""
    found_set = set(found)
    missing = [e for e in FROZEN_ELEMENTS if e not in found_set]
    if missing:
        return ('FSF-C1', 'جميع العناصر الـ 18 موجودة', 'FAIL',
                f'عناصر مفقودة ({len(missing)}): {" | ".join(missing)}',
                'أضف العناصر المفقودة بالاسم الصحيح')
    return ('FSF-C1', f'جميع العناصر الـ 18 موجودة', 'PASS',
            f'عُثر على {len(found_set)} عنصر', '')


def fsf_c2_correct_order(found: list[str]) -> tuple:
    """FSF-C2: ترتيب العناصر مطابق للتسلسل المجمَّد."""
    expected = [e for e in FROZEN_ELEMENTS if e in set(found)]
    actual   = [e for e in found if e in FROZEN_ELEMENTS_SET]
    # أزل التكرار مع حفظ الترتيب
    seen = set()
    actual_dedup = []
    for e in actual:
        if e not in seen:
            seen.add(e)
            actual_dedup.append(e)

    if actual_dedup == expected:
        return ('FSF-C2', 'ترتيب العناصر صحيح', 'PASS',
                f'{len(actual_dedup)} عنصر بالترتيب الصحيح', '')

    # ابحث عن أول انحراف
    for i, (exp, act) in enumerate(zip(expected, actual_dedup)):
        if exp != act:
            return ('FSF-C2', 'ترتيب العناصر', 'FAIL',
                    f'موضع {i+1}: توقعنا [{exp}] وجدنا [{act}]',
                    f'أعد ترتيب العناصر وفق التسلسل المجمَّد (18 عنصرًا)')
    # طول مختلف
    return ('FSF-C2', 'ترتيب العناصر', 'FAIL',
            f'العدد الفعلي ({len(actual_dedup)}) يختلف عن المتوقع ({len(expected)})',
            'تحقق من اكتمال جميع العناصر')


def fsf_c3_no_duplicate_elements(found: list[str]) -> tuple:
    """FSF-C3: لا تكرار في العناصر — كل عنصر يظهر مرة واحدة فقط."""
    seen: dict[str, int] = {}
    for e in found:
        seen[e] = seen.get(e, 0) + 1
    dups = {e: c for e, c in seen.items() if c > 1}
    if dups:
        detail = ' | '.join(f'[{e}] × {c}' for e, c in dups.items())
        return ('FSF-C3', 'لا تكرار في العناصر', 'FAIL',
                f'عناصر مكررة: {detail}',
                'احذف النسخة الزائدة من كل عنصر مكرر')
    return ('FSF-C3', 'لا تكرار في العناصر', 'PASS', '', '')


def fsf_c4_courses_count(lines: list[str]) -> tuple:
    """FSF-C4 / ELEMENT SHAPE LOCK: عدد الدورات الداعمة = 5."""
    section = extract_section(lines, 'الدورات الداعمة')
    bullet_links = [l for _, l in section if re.match(r'^\s*\*\s+', l) and re.search(r'\]\(https?://', l)]
    count = len(bullet_links)
    if count == REQUIRED_COURSES:
        return ('FSF-C4', f'الدورات الداعمة: العدد {REQUIRED_COURSES}', 'PASS',
                f'{count} دورة', '')
    drift = abs(count - REQUIRED_COURSES) / REQUIRED_COURSES
    verdict = 'FAIL_STRUCTURE_DRIFT' if drift > 0.15 else 'FAIL'
    return ('FSF-C4', f'الدورات الداعمة: يجب أن تكون {REQUIRED_COURSES}', verdict,
            f'العدد الفعلي: {count} (انحراف {drift:.0%})',
            f'أضف أو احذف دورات حتى يصبح العدد {REQUIRED_COURSES} بالضبط')


def fsf_c5_certs_count(lines: list[str]) -> tuple:
    """FSF-C5 / ELEMENT SHAPE LOCK: عدد الشهادات المهنية = 4 بالضبط."""
    section = extract_section(lines, 'الشهادات المهنية الاحترافية')
    bullet_links = [l for _, l in section if re.match(r'^\s*\*\s+', l) and re.search(r'\]\(https?://', l)]
    count = len(bullet_links)
    if count == REQUIRED_CERTS:
        return ('FSF-C5', f'الشهادات المهنية: العدد {REQUIRED_CERTS} بالضبط', 'PASS',
                f'{count} شهادة', '')
    drift = abs(count - REQUIRED_CERTS) / REQUIRED_CERTS
    verdict = 'FAIL_STRUCTURE_DRIFT' if drift > 0.15 else 'FAIL'
    return ('FSF-C5', f'الشهادات المهنية: يجب أن تكون {REQUIRED_CERTS} بالضبط', verdict,
            f'العدد الفعلي: {count} (انحراف {drift:.0%})',
            f'عدّل عدد الشهادات ليصبح {REQUIRED_CERTS} بالضبط — لا أقل ولا أكثر')


def fsf_c6_acceptance_table_columns(lines: list[str]) -> tuple:
    """FSF-C6 / ELEMENT SHAPE LOCK: جدول مدى القبول يحتوي 4 أعمدة."""
    section = extract_section(lines, 'جدول مدى قبول التخصصات')
    table_rows = [l for _, l in section if l.strip().startswith('|')]
    if not table_rows:
        return ('FSF-C6', 'جدول مدى القبول موجود', 'FAIL',
                'لم يُعثر على جدول (أسطر تبدأ بـ |)',
                'أضف جدول مدى قبول التخصصات بـ 4 أعمدة')
    # عدد الأعمدة من السطر الأول (Header)
    header = table_rows[0]
    cols = len([c for c in header.split('|') if c.strip()])
    if cols == TABLE_COLUMNS:
        return ('FSF-C6', f'جدول مدى القبول: {TABLE_COLUMNS} أعمدة', 'PASS',
                f'{cols} أعمدة', '')
    return ('FSF-C6', f'جدول مدى القبول: يجب أن يكون {TABLE_COLUMNS} أعمدة', 'FAIL',
            f'عُثر على {cols} عمود',
            f'عدّل الجدول ليحتوي {TABLE_COLUMNS} أعمدة بالضبط')


def fsf_c7_no_assessment_in_conditions(lines: list[str]) -> tuple:
    """FSF-C7 / CONTENT CROSS-CONTAMINATION LOCK:
    الشروط والمؤهلات لا تحتوي تسميات قبل/بعد التعيين."""
    pattern = r'<span class="condition-label">(قبل التعيين|بعد التعيين)'
    section = extract_section(lines, 'الشروط والمؤهلات')
    violations = []
    for lineno, line in section:
        if re.search(pattern, line):
            violations.append(lineno)
    if violations:
        return ('FSF-C7', 'CROSS-CONTAMINATION: لا تسميات قبل/بعد التعيين في الشروط', 'FAIL',
                f'سطور {violations}: محتوى التقييم دخل عنصر الشروط',
                'انقل "قبل التعيين/بعد التعيين" إلى عنصر متطلبات التقييم والتهيئة المهنية')
    return ('FSF-C7', 'CROSS-CONTAMINATION: الشروط نظيفة من محتوى التقييم', 'PASS', '', '')


def fsf_c8_cross_contamination(lines: list[str]) -> tuple:
    """FSF-C8 / CONTENT CROSS-CONTAMINATION LOCK:
    فحص التلوث المتقاطع لجميع العناصر الحساسة."""
    violations = []
    for element, pattern, description in CROSS_CONTAMINATION_RULES:
        section = extract_section(lines, element)
        for lineno, line in section:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append((element, lineno, description))

    if violations:
        detail = ' | '.join(f'[{e}] سطر {n}' for e, n, _ in violations[:6])
        descs  = list({d for _, _, d in violations})
        return ('FSF-C8', 'CROSS-CONTAMINATION LOCK', 'FAIL',
                f'{len(violations)} انتهاك: {detail}',
                'انقل المحتوى إلى العنصر الصحيح: ' + ' | '.join(descs[:2]))
    return ('FSF-C8', 'CROSS-CONTAMINATION LOCK: لا تلوث بين العناصر', 'PASS', '', '')


def fsf_c9_element_shape_programs(lines: list[str]) -> tuple:
    """FSF-C9 / ELEMENT SHAPE LOCK:
    برامج التأهيل — كل سطر يبدأ بـ * ويحتوي رابطاً ووصفاً."""
    section = extract_section(lines, 'برامج التأهيل المعتمدة')
    bullets = [l for _, l in section if l.strip().startswith('*')]
    if not bullets:
        return ('FSF-C9', 'برامج التأهيل: عناصر موجودة', 'FAIL',
                'لم يُعثر على نقاط في برامج التأهيل',
                'أضف برامج التأهيل بصيغة: * [اسم](رابط): وصف')
    violations = []
    for i, b in enumerate(bullets, 1):
        has_link    = bool(re.search(r'\]\(https?://', b))
        has_colon   = ':' in b
        if not has_link or not has_colon:
            violations.append(i)
    if violations:
        return ('FSF-C9', 'ELEMENT SHAPE: شكل سطور برامج التأهيل', 'FAIL',
                f'سطور {violations} تفتقر إلى رابط أو وصف بعد (:)',
                'الصيغة الصحيحة: * [اسم البرنامج — الجهة](https://...): السبب والفائدة')
    return ('FSF-C9', 'ELEMENT SHAPE: شكل برامج التأهيل صحيح', 'PASS',
            f'{len(bullets)} برنامج بصيغة صحيحة', '')


def fsf_c10_conditions_has_required_fields(lines: list[str]) -> tuple:
    """FSF-C10 / ELEMENT SHAPE LOCK:
    الشروط والمؤهلات تحتوي الحقول الأساسية المتوقعة."""
    section = extract_section(lines, 'الشروط والمؤهلات')
    text = ' '.join(l for _, l in section)
    required_patterns = [
        (r'بكالوريوس|ليسانس|درجة علمية|مؤهل', 'درجة علمية / مؤهل'),
        (r'تخصص|قانون|شريعة|مالية|حقوق|إدارة', 'تخصص أكاديمي'),
        (r'سعودي|الجنسية', 'شرط الجنسية'),
    ]
    missing = []
    for pattern, label in required_patterns:
        if not re.search(pattern, text, re.IGNORECASE):
            missing.append(label)
    if len(missing) >= 2:
        return ('FSF-C10', 'ELEMENT SHAPE: الشروط تحتوي الحقول الأساسية', 'FAIL',
                f'حقول مفقودة: {" | ".join(missing)}',
                'تأكد من وجود المؤهل والتخصص وشرط الجنسية في عنصر الشروط والمؤهلات')
    return ('FSF-C10', 'ELEMENT SHAPE: الشروط والمؤهلات تحتوي الحقول الأساسية', 'PASS', '', '')


def fsf_c11_assessment_has_pre_post(lines: list[str]) -> tuple:
    """FSF-C11 / ELEMENT SHAPE LOCK:
    متطلبات التقييم تحتوي تسميات قبل/بعد التعيين بالشكل الصحيح."""
    section = extract_section(lines, 'متطلبات التقييم والتهيئة المهنية')
    text = ' '.join(l for _, l in section)
    has_before = bool(re.search(r'قبل التعيين', text))
    has_after  = bool(re.search(r'بعد التعيين', text))
    if has_before and has_after:
        return ('FSF-C11', 'ELEMENT SHAPE: متطلبات التقييم تحتوي قبل/بعد التعيين', 'PASS', '', '')
    missing = []
    if not has_before:
        missing.append('قبل التعيين')
    if not has_after:
        missing.append('بعد التعيين')
    return ('FSF-C11', 'ELEMENT SHAPE: متطلبات التقييم ناقصة', 'FAIL',
            f'مفقود: {" و ".join(missing)}',
            'أضف فقرتي "قبل التعيين" و"بعد التعيين" باستخدام <span class="condition-label">')


# ── تشغيل كامل ───────────────────────────────────────────────────────────────

FREEZE_CHECKS = [
    fsf_c1_all_elements_present,
    fsf_c2_correct_order,
    fsf_c3_no_duplicate_elements,
    fsf_c4_courses_count,
    fsf_c5_certs_count,
    fsf_c6_acceptance_table_columns,
    fsf_c7_no_assessment_in_conditions,
    fsf_c8_cross_contamination,
    fsf_c9_element_shape_programs,
    fsf_c10_conditions_has_required_fields,
    fsf_c11_assessment_has_pre_post,
]

DRIFT_VERDICTS = frozenset({'FAIL_STRUCTURE_DRIFT', 'FAIL'})


def run_freeze_checks(path: str) -> tuple[list, list, list]:
    """
    يُنفّذ جميع فحوص CONTENT STRUCTURE FREEZE CHECK v1.0.
    يُعيد (passed, failed, drift_fails).
    """
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    found_elements = extract_elements_order(lines)

    passed = []
    failed = []
    drift_fails = []

    for fn in FREEZE_CHECKS:
        try:
            # الفحوص C1-C3 تعتمد على found_elements، باقيها على lines
            if fn in (fsf_c1_all_elements_present, fsf_c2_correct_order, fsf_c3_no_duplicate_elements):
                result = fn(found_elements)
            else:
                result = fn(lines)
        except Exception as e:
            result = (fn.__name__, 'خطأ في الفحص', 'FAIL', str(e), 'تحقق من بنية الملف')

        code, label, verdict, detail, fix = result
        entry = {'code': code, 'label': label, 'verdict': verdict, 'detail': detail, 'fix': fix}

        if verdict == 'PASS':
            passed.append(entry)
        elif verdict == 'FAIL_STRUCTURE_DRIFT':
            drift_fails.append(entry)
            failed.append(entry)
        else:
            failed.append(entry)

    return passed, failed, drift_fails


def print_freeze_report(path: str, passed: list, failed: list, drift_fails: list) -> bool:
    total = len(passed) + len(failed)
    ok = len(failed) == 0

    print('=' * 65)
    print('  CONTENT STRUCTURE FREEZE CHECK v1.0')
    print('  ELEMENT SHAPE LOCK + CONTENT CROSS-CONTAMINATION LOCK')
    print(f'  الملف: {Path(path).name}')
    print('=' * 65)

    for e in passed:
        print(f'  ✅ [{e["code"]}] {e["label"]}')
        if e['detail']:
            print(f'       → {e["detail"]}')

    if failed:
        boundary = [e for e in failed if e['verdict'] == 'FAIL_STRUCTURE_DRIFT']
        others   = [e for e in failed if e['verdict'] != 'FAIL_STRUCTURE_DRIFT']

        if boundary:
            print(f'\n  📐 FAIL_STRUCTURE_DRIFT — انحراف بنيوي ({len(boundary)}):')
            for e in boundary:
                print(f'\n  📐 [{e["code"]}] {e["label"]}')
                print(f'       السبب: {e["detail"]}')
                if e['fix']:
                    print(f'       🔧 المطلوب: {e["fix"]}')

        if others:
            print(f'\n  ❌ فحوص فاشلة ({len(others)}):')
            for e in others:
                print(f'\n  ❌ [{e["code"]}] {e["label"]}')
                print(f'       السبب: {e["detail"]}')
                if e['fix']:
                    print(f'       🔧 المطلوب: {e["fix"]}')

    print(f'\n  الإجمالي: {total} | ✅ {len(passed)} | ❌ {len(failed)}')
    if drift_fails:
        print(f'  FAIL_STRUCTURE_DRIFT: {len(drift_fails)}')
    print(f'\n  النتيجة: {"PASS — البنية مطابقة للنموذج المجمَّد" if ok else "FAIL — لا يجوز توليد PDF"}')
    print('=' * 65)
    return ok


def main():
    parser = argparse.ArgumentParser(
        description='CONTENT STRUCTURE FREEZE CHECK v1.0'
    )
    parser.add_argument('files', nargs='+', help='ملفات Markdown للفحص')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    all_ok = True
    for path in args.files:
        passed, failed, drift = run_freeze_checks(path)
        ok = print_freeze_report(path, passed, failed, drift)
        if not ok:
            all_ok = False

    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
