"""
scope_guard.py — حارس النطاق لبطاقات مشروع الشريعة
يُولِّد قفل هاش SHA-256 لكل عنصر ويتحقق من عدم تغيير المحتوى بعد الاعتماد.

الاستخدام:
  python scripts/scope_guard.py --card <path> --generate-lock --output <lock_path>
  python scripts/scope_guard.py --card <path> --lock <lock_path> [--allow "element1"] [--allow "element2"]
"""

import sys
import os
import re
import json
import hashlib
import argparse
import subprocess

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

ELEMENTS_SET = set(ELEMENTS_ORDER)


def extract_elements(card_path):
    """
    قراءة ملف البطاقة واستخراج محتوى كل عنصر من العناصر الـ18.
    يُعيد dict: اسم_العنصر → محتوى_العنصر (string)
    """
    with open(card_path, encoding='utf-8') as f:
        lines = f.readlines()

    elements = {}
    current_element = None
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped in ELEMENTS_SET:
            # حفظ العنصر السابق
            if current_element is not None:
                elements[current_element] = _normalize_content(current_lines)
            current_element = stripped
            current_lines = []
        else:
            if current_element is not None:
                current_lines.append(line)

    # حفظ آخر عنصر
    if current_element is not None:
        elements[current_element] = _normalize_content(current_lines)

    return elements


def _normalize_content(lines):
    """تنظيف المحتوى: إزالة المسافات الزائدة من نهاية كل سطر والربط بسطر جديد."""
    normalized = [l.rstrip() for l in lines]
    # حذف الأسطر الفارغة من البداية والنهاية
    while normalized and not normalized[0]:
        normalized.pop(0)
    while normalized and not normalized[-1]:
        normalized.pop()
    return '\n'.join(normalized)


def hash_element(content):
    """حساب SHA-256 لمحتوى العنصر."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def get_current_commit(card_path):
    """الحصول على آخر commit hash للملف."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%h', card_path],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.abspath(card_path))
        )
        return result.stdout.strip() or 'unknown'
    except Exception:
        return 'unknown'


def generate_lock(card_path, output_path, locked_at='2026-06-13'):
    """توليد ملف القفل."""
    elements = extract_elements(card_path)
    stem = os.path.splitext(os.path.basename(card_path))[0]
    locked_commit = get_current_commit(card_path)

    hashes = {}
    for elem in ELEMENTS_ORDER:
        content = elements.get(elem, '')
        hashes[elem] = hash_element(content)

    lock_data = {
        'card_name': stem,
        'locked_commit': locked_commit,
        'locked_at': locked_at,
        'note': 'قفل النطاق — يمنع التغييرات الجانبية بعد الاعتماد',
        'elements': hashes,
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(lock_data, f, ensure_ascii=False, indent=2)

    return lock_data


def check_css_template_changes(locked_commit, repo_root):
    """
    تحقق من تغيير ملفات CSS أو القوالب منذ locked_commit.
    يُعيد قائمة الملفات المتغيرة.
    """
    if not locked_commit or locked_commit == 'unknown':
        return []
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', locked_commit, 'HEAD'],
            capture_output=True, text=True, cwd=repo_root
        )
        changed = result.stdout.strip().splitlines()
        sensitive = [
            f for f in changed
            if f.startswith('assets/css/') or f.startswith('templates/')
        ]
        return sensitive
    except Exception:
        return []


def run_scope_check(card_path, lock_path, allowed_elements=None):
    """
    تحقق من تطابق هاشات العناصر مع ملف القفل.

    يُعيد قائمة من 5-tuples:
    (id, label, status, detail, fix_hint)

    إذا لم يكن ملف القفل موجودًا → PASS (بطاقة جديدة)
    إذا كان موجودًا → مقارنة الهاشات
    """
    allowed = set(allowed_elements or [])
    results = []

    # ── حالة: لا يوجد ملف قفل ──────────────────────────────────────────────────
    if not os.path.exists(lock_path):
        results.append((
            'C23',
            'Scope Guard — لا ملف قفل',
            'PASS',
            'بطاقة جديدة — لا قفل موجود بعد',
            'شغّل --generate-lock بعد الاعتماد لإنشاء القفل'
        ))
        return results

    # ── تحميل القفل ─────────────────────────────────────────────────────────────
    try:
        with open(lock_path, encoding='utf-8') as f:
            lock_data = json.load(f)
    except Exception as e:
        results.append((
            'C23',
            'Scope Guard — خطأ في قراءة القفل',
            'FAIL',
            f'تعذّر قراءة ملف القفل: {e}',
            'تحقق من صحة ملف JSON'
        ))
        return results

    locked_commit = lock_data.get('locked_commit', 'unknown')
    locked_hashes = lock_data.get('elements', {})

    # ── تحقق من CSS والقوالب ────────────────────────────────────────────────────
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(card_path)))
    changed_assets = check_css_template_changes(locked_commit, repo_root)
    if changed_assets:
        results.append((
            'C23-CSS',
            'Scope Guard — تغيير CSS/قوالب',
            'FAIL',
            f'ملفات تغيّرت منذ القفل ({locked_commit}): {changed_assets[:5]}',
            'راجع التغييرات في assets/css/ و templates/ وأعِد الاعتماد'
        ))
    else:
        results.append((
            'C23-CSS',
            'Scope Guard — لا تغيير في CSS/القوالب',
            'PASS',
            f'منذ القفل {locked_commit}: لا تغييرات في assets/css/ أو templates/',
            ''
        ))

    # ── مقارنة هاشات العناصر ────────────────────────────────────────────────────
    elements = extract_elements(card_path)
    changed_elements = []
    missing_in_lock = []

    for elem in ELEMENTS_ORDER:
        current_content = elements.get(elem, '')
        current_hash = hash_element(current_content)

        if elem not in locked_hashes:
            missing_in_lock.append(elem)
            continue

        locked_hash = locked_hashes[elem]
        if current_hash != locked_hash:
            if elem in allowed:
                # تغيير مسموح
                results.append((
                    'C23',
                    f'Scope Guard — تغيير مسموح: {elem}',
                    'PASS',
                    f'تغيّر الهاش (مسموح بـ --allow)',
                    ''
                ))
            else:
                changed_elements.append(elem)

    if missing_in_lock:
        results.append((
            'C23',
            'Scope Guard — عناصر غير مقفولة',
            'MANUAL',
            f'عناصر غير موجودة في القفل: {missing_in_lock}',
            'أعِد توليد القفل لتشمل جميع العناصر'
        ))

    if changed_elements:
        results.append((
            'C23',
            'Scope Guard — عناصر تغيّرت بعد القفل',
            'FAIL',
            f'عناصر مُعدَّلة بدون تصريح: {changed_elements}',
            'أضِف --allow "اسم_العنصر" لكل تغيير مقصود، أو أعِد توليد القفل بعد الاعتماد'
        ))
    elif not missing_in_lock:
        results.append((
            'C23',
            'Scope Guard — جميع العناصر مطابقة للقفل',
            'PASS',
            f'تحقّق من {len(ELEMENTS_ORDER)} عنصر — لا تغييرات',
            ''
        ))

    return results


def main():
    parser = argparse.ArgumentParser(description='حارس النطاق — scope_guard.py')
    parser.add_argument('--card', required=True, help='مسار ملف البطاقة MD')
    parser.add_argument('--generate-lock', action='store_true',
                        help='توليد ملف قفل جديد')
    parser.add_argument('--output', help='مسار ملف القفل الناتج (مع --generate-lock)')
    parser.add_argument('--lock', help='مسار ملف القفل للتحقق منه')
    parser.add_argument('--allow', action='append', default=[],
                        help='عنصر مسموح بتغييره (يمكن تكراره)')

    args = parser.parse_args()

    card_path = os.path.abspath(args.card)
    if not os.path.exists(card_path):
        print(f'❌ الملف غير موجود: {card_path}')
        sys.exit(1)

    if args.generate_lock:
        output_path = args.output
        if not output_path:
            stem = os.path.splitext(os.path.basename(card_path))[0]
            repo_root = os.path.dirname(os.path.dirname(card_path))
            output_path = os.path.join(repo_root, 'outputs', 'locks',
                                       f'{stem}_scope_lock.json')
        output_path = os.path.abspath(output_path)
        lock_data = generate_lock(card_path, output_path)
        print(f'✅ تم توليد ملف القفل: {output_path}')
        print(f'   card_name: {lock_data["card_name"]}')
        print(f'   locked_commit: {lock_data["locked_commit"]}')
        print(f'   locked_at: {lock_data["locked_at"]}')
        print(f'   عدد العناصر المقفولة: {len(lock_data["elements"])}')
        sys.exit(0)

    if args.lock:
        lock_path = os.path.abspath(args.lock)
        scope_results = run_scope_check(card_path, lock_path,
                                        allowed_elements=args.allow)
        print('=' * 60)
        print(f'  Scope Guard — {os.path.basename(card_path)}')
        print('=' * 60)
        overall = 'PASS'
        for r in scope_results:
            icon = {'PASS': '✅', 'FAIL': '❌', 'MANUAL': '⚠️ '}[r[2]]
            print(f'  {icon} [{r[0]}] {r[1]}')
            if r[3]:
                print(f'       → {r[3]}')
            if r[2] == 'FAIL':
                overall = 'FAIL'
        print('-' * 60)
        passed = sum(1 for r in scope_results if r[2] == 'PASS')
        failed = sum(1 for r in scope_results if r[2] == 'FAIL')
        manual = sum(1 for r in scope_results if r[2] == 'MANUAL')
        print(f'  النتيجة: {overall}  |  ✅ {passed}  ❌ {failed}  ⚠️  {manual}')
        print('=' * 60)
        sys.exit(0 if overall == 'PASS' else 1)

    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()
