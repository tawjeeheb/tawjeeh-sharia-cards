"""
validate_card_contract.py — فحص عقد محتوى البطاقة
يُطبّق قواعد contracts/card_content_contract.yaml على ملف MD.
الاستخدام: python scripts/validate_card_contract.py outputs/test_card_xxx.md
"""

import sys
import re
import os

# ── ثوابت (مرتبطة بالعقد مباشرة) ────────────────────────────────────────────

ELEMENTS_ORDER = [
    'المسميات المكافئة', 'التصنيف الوطني SSC', 'طبيعة العمل',
    'المهام الرئيسية', 'المرتبة والراتب', 'المزايا الوظيفية',
    'الشروط والمؤهلات', 'متطلبات التقييم والتهيئة المهنية',
    'الخبرات المطلوبة', 'برامج التأهيل المعتمدة', 'المهارات المطلوبة',
    'الدورات الداعمة', 'جهات التوظيف وطرق التقديم',
    'المسار الوظيفي والتطور المهني', 'الشهادات المهنية الاحترافية',
    'الملاحظات المهنية المتقدمة', 'النصائح العملية الإضافية',
    'جدول مدى قبول التخصصات',
]

ALLOWED_COURSE_DOMAINS = ['lms.doroob.sa', 'coursera.org', 'ethrai.sa']
COURSE_ELEMENT = 'الدورات الداعمة'
EMPLOYMENT_ELEMENT = 'جهات التوظيف وطرق التقديم'
CONDITIONS_ELEMENT = 'الشروط والمؤهلات'
CERTS_ELEMENT = 'الشهادات المهنية الاحترافية'
MUSAMMA_ELEMENT = 'المسميات المكافئة'

FORBIDDEN_EMPLOYMENT_HEADINGS = [
    'جهات سبق وأعلنت',
    'جهات توظف لوجود ممارسة/وحدات',
    'جهات توظف لوجود أدوات أو وحدات',
    'جهات مستحدثة/ناشئة',
    'جهات مستحدثة / ناشئة قليلة التنافس',
]

SECTOR_ORDER_KEYS = ['الحكومي', 'شبه الحكومي', 'الخاص', 'غير الربحي', 'المستقل']

FORBIDDEN_CONDITIONS_HEADINGS = ['شروط التخصصات الدقيقة']


# ── أدوات مساعدة ──────────────────────────────────────────────────────────────

def extract_section(lines, element_name):
    """استخرج سطور قسم معين بين عنوانه والعنصر التالي."""
    in_section = False
    section_lines = []
    for i, line in enumerate(lines):
        s = line.strip()
        if s == element_name:
            in_section = True
            continue
        if in_section:
            # أي عنصر رئيسي آخر = نهاية القسم
            if s in ELEMENTS_ORDER:
                break
            section_lines.append((i + 1, line))
    return section_lines


def arabic_word_count(text):
    """عدد الكلمات في نص (فراغات كفاصل)."""
    return len(text.strip().split())


def is_arabic_start(text):
    """هل يبدأ النص بحرف عربي؟"""
    text = text.strip()
    if not text:
        return False
    return bool(re.match(r'^[؀-ۿ]', text))


# ── الفحوصات ──────────────────────────────────────────────────────────────────

def check_c11_no_old_employment_headings(lines):
    """C11: لا فئات قديمة كعناوين داخل جهات التوظيف."""
    section = extract_section(lines, EMPLOYMENT_ELEMENT)
    violations = []
    for lineno, line in section:
        stripped = line.strip()
        for forbidden in FORBIDDEN_EMPLOYMENT_HEADINGS:
            if stripped == forbidden:
                violations.append((lineno, stripped))
                break
    if violations:
        detail = ' | '.join(f'سطر {n}: "{t}"' for n, t in violations)
        return ('C11', 'لا فئات قديمة كعناوين في جهات التوظيف', 'FAIL',
                f'فئات محظورة: {detail}',
                'احذف هذه العناوين — الفئات الداخلية أدوات بحث لا تظهر في الإخراج النهائي')
    return ('C11', 'لا فئات قديمة كعناوين في جهات التوظيف', 'PASS', '', '')


def check_c12_sector_headings_have_parens(lines):
    """C12: عناوين القطاعات تحتوي المسميات بين قوسين."""
    section = extract_section(lines, EMPLOYMENT_ELEMENT)
    violations = []
    for lineno, line in section:
        stripped = line.strip()
        # سطر قطاع = يبدأ بـ "القطاع"
        if stripped.startswith('القطاع'):
            # يجب أن يحتوي قوسين
            if '(' not in stripped or ')' not in stripped:
                violations.append((lineno, stripped))
    if violations:
        detail = ' | '.join(f'سطر {n}: "{t}"' for n, t in violations[:5])
        return ('C12', 'عناوين القطاعات تحتوي المسميات بين قوسين', 'FAIL',
                f'عناوين بلا مسميات: {detail}',
                'أضف المسميات المناسبة بين قوسين مثل: القطاع الحكومي (مسمى1، مسمى2)')
    if any(line.strip().startswith('القطاع') for _, line in section):
        return ('C12', 'عناوين القطاعات تحتوي المسميات بين قوسين', 'PASS', '', '')
    return ('C12', 'عناوين القطاعات — لا قطاعات في هذه البطاقة', 'PASS', '', '')


def check_c13_sector_order(lines):
    """C13: ترتيب القطاعات ثابت: حكومي→شبه حكومي→خاص→غير ربحي→مستقل."""
    section = extract_section(lines, EMPLOYMENT_ELEMENT)
    # ترتيب الفحص من الأطول للأقصر لتفادي "الحكومي" يتطابق مع "شبه الحكومي"
    _detect_order = sorted(SECTOR_ORDER_KEYS, key=len, reverse=True)
    found_sectors = []
    for _, line in section:
        s = line.strip()
        if s.startswith('القطاع'):
            for key in _detect_order:
                if ('القطاع ' + key) in s or s == ('القطاع ' + key):
                    found_sectors.append(key)
                    break
    # تحقق من الترتيب
    ordered = [k for k in SECTOR_ORDER_KEYS if k in found_sectors]
    if found_sectors == ordered:
        return ('C13', 'ترتيب القطاعات صحيح', 'PASS',
                f'القطاعات: {" ← ".join(found_sectors)}', '')
    return ('C13', 'ترتيب القطاعات', 'FAIL',
            f'الترتيب الفعلي: {found_sectors} | المطلوب: {ordered}',
            'أعد ترتيب القطاعات: حكومي → شبه حكومي → خاص → غير ربحي → مستقل')


def check_c14_courses_count(lines):
    """C14: عدد الدورات الداعمة يساوي 5."""
    section = extract_section(lines, COURSE_ELEMENT)
    course_lines = [l for _, l in section if re.match(r'^\s*\*\s+', l) and 'دورة' in l]
    count = len(course_lines)
    if count == 5:
        return ('C14', 'الدورات الداعمة: العدد 5', 'PASS',
                f'عُثر على {count} دورات', '')
    return ('C14', 'الدورات الداعمة: العدد يجب أن يكون 5', 'FAIL',
            f'العدد الفعلي: {count}',
            f'أضف أو احذف دورات حتى يصبح العدد 5 بالضبط (الحالي: {count})')


def check_c15_courses_platforms(lines):
    """C15: منصات الدورات من المنصات المعتمدة فقط: دروب/Coursera/إثرائي."""
    section = extract_section(lines, COURSE_ELEMENT)
    violations = []
    for lineno, line in section:
        if not (re.match(r'^\s*\*\s+', line) and 'دورة' in line):
            continue
        # استخرج جميع الروابط من هذا السطر
        urls = re.findall(r'\]\((https?://[^)]+)\)', line)
        for url in urls:
            allowed = any(domain in url for domain in ALLOWED_COURSE_DOMAINS)
            if not allowed:
                violations.append((lineno, url[:60]))
    if violations:
        detail = ' | '.join(f'سطر {n}: {u}' for n, u in violations[:5])
        return ('C15', 'منصات الدورات معتمدة (دروب/Coursera/إثرائي)', 'FAIL',
                f'روابط من منصات غير معتمدة: {detail}',
                f'المنصات المعتمدة فقط: {", ".join(ALLOWED_COURSE_DOMAINS)}')
    return ('C15', 'منصات الدورات معتمدة (دروب/Coursera/إثرائي)', 'PASS', '', '')


def check_c16_course_names_arabic(lines):
    """C16: أسماء الدورات تبدأ بحرف عربي."""
    section = extract_section(lines, COURSE_ELEMENT)
    violations = []
    for lineno, line in section:
        if not (re.match(r'^\s*\*\s+', line) and 'دورة' in line):
            continue
        # استخرج النص داخل [نص] في رابط الدورة
        m = re.search(r'دورة\s+\[([^\]]+)\]', line)
        if m:
            name = m.group(1).strip()
            if not is_arabic_start(name):
                violations.append((lineno, name[:50]))
    if violations:
        detail = ' | '.join(f'سطر {n}: "{t}"' for n, t in violations)
        return ('C16', 'أسماء الدورات عربية', 'FAIL',
                f'أسماء تبدأ بغير العربية: {detail}',
                'غيّر اسم الدورة ليبدأ بحرف عربي — اسم المنصة لا يُدرج داخل اسم الدورة')
    return ('C16', 'أسماء الدورات عربية', 'PASS', '', '')


def check_c17_course_reason_length(lines):
    """C17: السبب بعد النقطتين في الدورة لا يتجاوز 5 كلمات."""
    section = extract_section(lines, COURSE_ELEMENT)
    violations = []
    for lineno, line in section:
        if not (re.match(r'^\s*\*\s+', line) and 'دورة' in line):
            continue
        # الصيغة: دورة [اسم](رابط): سبب
        # نبحث عن النص بعد ):
        m = re.search(r'\)\s*:\s*(.+)$', line.rstrip())
        if m:
            reason = m.group(1).strip()
            # أزل الروابط إن وجدت
            reason_clean = re.sub(r'\[[^\]]*\]\([^)]*\)', '', reason).strip()
            word_count = arabic_word_count(reason_clean)
            if word_count > 5:
                violations.append((lineno, reason_clean[:60], word_count))
    if violations:
        detail = ' | '.join(f'سطر {n}: "{r}" ({w} كلمة)' for n, r, w in violations)
        return ('C17', 'سبب الدورة لا يتجاوز 5 كلمات', 'FAIL',
                f'أسباب طويلة: {detail}',
                'اختصر السبب إلى 5 كلمات كحد أقصى بعد النقطتين')
    return ('C17', 'سبب الدورة لا يتجاوز 5 كلمات', 'PASS', '', '')


def check_c18_certs_support_status(lines):
    """C18: كل شهادة مهنية تنتهي بـ (مدعومة) أو (غير مدعومة)."""
    section = extract_section(lines, CERTS_ELEMENT)
    violations = []
    for lineno, line in section:
        if not re.match(r'^\s*\*\s+', line):
            continue
        stripped = line.strip()
        if not stripped:
            continue
        # يجب أن ينتهي بـ (مدعومة) أو (غير مدعومة)
        if not re.search(r'\((مدعومة|غير مدعومة)\)\s*$', stripped):
            violations.append((lineno, stripped[:80]))
    if violations:
        detail = ' | '.join(f'سطر {n}' for n, _ in violations[:5])
        return ('C18', 'حالة دعم الشهادات (مدعومة/غير مدعومة)', 'FAIL',
                f'شهادات بلا حالة دعم: {detail}',
                'أضف (مدعومة) أو (غير مدعومة) في نهاية كل سطر شهادة')
    return ('C18', 'حالة دعم الشهادات (مدعومة/غير مدعومة)', 'PASS', '', '')


def check_c19_no_archived_prompt_refs(lines):
    """C19: البطاقة لا تحتوي إحالة لبرومبتات مؤرشفة."""
    violations = []
    for i, line in enumerate(lines, 1):
        if 'prompts/archive/' in line:
            violations.append((i, line.strip()[:80]))
    if violations:
        detail = ' | '.join(f'سطر {n}: "{t}"' for n, t in violations[:3])
        return ('C19', 'لا إحالة لبرومبتات مؤرشفة', 'FAIL',
                f'إحالات محظورة: {detail}',
                'احذف أي إحالة لـ prompts/archive/ من البطاقة — الأرشيف للمراجعة التدقيقية فقط')
    return ('C19', 'لا إحالة لبرومبتات مؤرشفة', 'PASS', '', '')


def check_c20_conditions_no_specialization_heading(lines):
    """C20: الشروط والمؤهلات لا تحتوي عنوان شروط التخصصات الدقيقة."""
    section = extract_section(lines, CONDITIONS_ELEMENT)
    violations = []
    for lineno, line in section:
        stripped = line.strip()
        for forbidden in FORBIDDEN_CONDITIONS_HEADINGS:
            if forbidden in stripped:
                violations.append((lineno, stripped[:80]))
                break
    if violations:
        detail = ' | '.join(f'سطر {n}: "{t}"' for n, t in violations)
        return ('C20', 'الشروط: لا شروط تخصصات دقيقة', 'FAIL',
                f'عناوين محظورة: {detail}',
                'احذف فقرة "شروط التخصصات الدقيقة" من عنصر الشروط والمؤهلات')
    return ('C20', 'الشروط: لا شروط تخصصات دقيقة', 'PASS', '', '')


def check_c21_musamma_single_line(lines):
    """C21: المسميات المكافئة في سطر واحد بعد العنوان مباشرة."""
    section = extract_section(lines, MUSAMMA_ELEMENT)
    non_empty = [(n, l) for n, l in section if l.strip()]
    if not non_empty:
        return ('C21', 'المسميات المكافئة موجودة', 'FAIL',
                'عنصر المسميات المكافئة فارغ',
                'أضف المسميات في سطر واحد بعد العنوان مباشرة')
    if len(non_empty) > 1:
        extra = [f'سطر {n}' for n, _ in non_empty[1:]]
        return ('C21', 'المسميات المكافئة في سطر واحد', 'FAIL',
                f'عُثر على {len(non_empty)} سطور غير فارغة: {", ".join(extra)}',
                'ادمج المسميات في سطر واحد مفصولة بفاصلة')
    return ('C21', 'المسميات المكافئة في سطر واحد', 'PASS', '', '')


def check_c22_employment_sector_bullets(lines):
    """C22: داخل كل قطاع من 3 إلى 5 نقاط."""
    section = extract_section(lines, EMPLOYMENT_ELEMENT)
    current_sector = None
    sector_bullets = {}
    for _, line in section:
        stripped = line.strip()
        if stripped.startswith('القطاع'):
            current_sector = stripped
            sector_bullets[current_sector] = 0
        elif current_sector and re.match(r'^\*\s+', stripped):
            sector_bullets[current_sector] += 1
    violations = []
    for sector, count in sector_bullets.items():
        if count < 3:
            violations.append(f'"{sector}": {count} نقطة (الحد الأدنى 3)')
        elif count > 5:
            violations.append(f'"{sector}": {count} نقطة (الحد الأقصى 5)')
    if violations:
        detail = ' | '.join(violations)
        return ('C22', 'نقاط كل قطاع بين 3 و5', 'FAIL',
                detail,
                'عدّل عدد النقاط داخل القطاع المخالف ليكون بين 3 و5')
    if sector_bullets:
        summary = ', '.join(f'{k.split("(")[0].strip()}:{v}' for k, v in sector_bullets.items())
        return ('C22', 'نقاط كل قطاع بين 3 و5', 'PASS', summary, '')
    return ('C22', 'نقاط القطاعات', 'PASS', 'لا قطاعات', '')


# ── تشغيل كل الفحوصات ─────────────────────────────────────────────────────────

def run_contract_checks(path):
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    checks = [
        check_c11_no_old_employment_headings,
        check_c12_sector_headings_have_parens,
        check_c13_sector_order,
        check_c14_courses_count,
        check_c15_courses_platforms,
        check_c16_course_names_arabic,
        check_c17_course_reason_length,
        check_c18_certs_support_status,
        check_c19_no_archived_prompt_refs,
        check_c20_conditions_no_specialization_heading,
        check_c21_musamma_single_line,
        check_c22_employment_sector_bullets,
    ]

    results = []
    for check_fn in checks:
        try:
            r = check_fn(lines)
            # r = (id, label, status, detail, fix_hint)
            results.append(r)
        except Exception as e:
            results.append((check_fn.__name__, f'خطأ في الفحص', 'FAIL',
                            str(e), 'تحقق من بنية الملف'))

    return results


def print_contract_report(results, path):
    passed = sum(1 for r in results if r[2] == 'PASS')
    failed = sum(1 for r in results if r[2] == 'FAIL')
    overall = 'PASS' if failed == 0 else 'FAIL'

    print('=' * 60)
    print(f'  فحص العقد — {os.path.basename(path)}')
    print('=' * 60)
    for r in results:
        icon = {'PASS': '✅', 'FAIL': '❌', 'MANUAL': '⚠️ '}.get(r[2], '?')
        print(f'  {icon} [{r[0]}] {r[1]}')
        if r[3]:
            print(f'       → {r[3]}')
        if r[2] == 'FAIL' and len(r) > 4 and r[4]:
            print(f'       🔧 المطلوب: {r[4]}')
    print('-' * 60)
    print(f'  العقد: {overall}  |  ✅ {passed}  ❌ {failed}  من {len(results)}')
    print('=' * 60)
    return overall, passed, failed


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('الاستخدام: python scripts/validate_card_contract.py <مسار_البطاقة>')
        sys.exit(1)
    path = os.path.abspath(sys.argv[1])
    if not os.path.exists(path):
        print(f'خطأ: الملف غير موجود: {path}')
        sys.exit(1)
    results = run_contract_checks(path)
    overall, passed, failed = print_contract_report(results, path)
    sys.exit(0 if overall == 'PASS' else 1)
