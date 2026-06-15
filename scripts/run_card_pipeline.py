"""
run_card_pipeline.py — One-Click Card Pipeline
يُشغّل جميع خطوات إنتاج البطاقة والفحص والاعتماد بأمر واحد.

الاستخدام:
  python scripts/run_card_pipeline.py --card outputs/test_card_009_*.md
  python scripts/run_card_pipeline.py --card outputs/test_card_009_*.md --build
  python scripts/run_card_pipeline.py --validate-all
"""

import sys
import os
import re
import json
import argparse
import subprocess
import glob
from datetime import date

# إضافة مجلد scripts إلى المسار
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _scripts_dir)

REPO_ROOT = os.path.dirname(_scripts_dir)
OUTPUTS_DIR = os.path.join(REPO_ROOT, 'outputs')
PDF_DIR = os.path.join(OUTPUTS_DIR, 'pdf')
LOCKS_DIR = os.path.join(OUTPUTS_DIR, 'locks')
MANIFESTS_DIR = os.path.join(REPO_ROOT, 'cards_manifest')

# ── استيراد الأنظمة الفرعية ────────────────────────────────────────────────

try:
    from quality_gate import run_checks, print_report, build_md_report
    _QG_AVAILABLE = True
except ImportError:
    _QG_AVAILABLE = False

try:
    from scope_guard import run_scope_check
    _SG_AVAILABLE = True
except ImportError:
    _SG_AVAILABLE = False

try:
    from validate_pdf_links import validate_pdf_links
    _VPL_AVAILABLE = True
except ImportError:
    _VPL_AVAILABLE = False


# ── أدوات مساعدة ──────────────────────────────────────────────────────────────

def find_card_path(card_ref):
    """حوّل رقم بطاقة أو مسار جزئي إلى مسار كامل."""
    if os.path.exists(card_ref):
        return os.path.abspath(card_ref)
    # جرب pattern matching
    pattern = os.path.join(OUTPUTS_DIR, f'*{card_ref}*.md')
    matches = [m for m in glob.glob(pattern)
               if not m.startswith(os.path.join(OUTPUTS_DIR, 'golden'))
               and not m.startswith(os.path.join(OUTPUTS_DIR, 'archive'))]
    if len(matches) == 1:
        return os.path.abspath(matches[0])
    if len(matches) > 1:
        # فضّل المطابقة الأدق
        exact = [m for m in matches if f'_{card_ref}_' in os.path.basename(m) or
                 os.path.basename(m).startswith(f'test_card_{card_ref}')]
        if len(exact) == 1:
            return os.path.abspath(exact[0])
        print(f'⚠️  تطابقات متعددة: {[os.path.basename(m) for m in matches]}')
        return None
    return None


def find_lock(card_path):
    stem = os.path.splitext(os.path.basename(card_path))[0]
    return os.path.join(LOCKS_DIR, f'{stem}_scope_lock.json')


def find_manifest(card_path):
    stem = os.path.splitext(os.path.basename(card_path))[0]
    # استخرج رقم البطاقة
    m = re.match(r'test_card_(\d+)', stem)
    if m:
        num = m.group(1)
        path = os.path.join(MANIFESTS_DIR, f'test_card_{num}.yaml')
        if os.path.exists(path):
            return path
    return os.path.join(MANIFESTS_DIR, f'{stem}.yaml')


def html_path(card_path):
    stem = os.path.splitext(os.path.basename(card_path))[0]
    return os.path.join(PDF_DIR, f'{stem}.html')


def pdf_path(card_path):
    stem = os.path.splitext(os.path.basename(card_path))[0]
    return os.path.join(PDF_DIR, f'{stem}.pdf')


def evidence_path(card_path):
    stem = os.path.splitext(os.path.basename(card_path))[0]
    return os.path.join(OUTPUTS_DIR, 'evidence', f'{stem}_certifications_support_audit.md')


# ── خطوة: توليد HTML/PDF ──────────────────────────────────────────────────────

def step_build(card_path):
    """يولّد HTML وPDF من ملف MD."""
    convert_script = os.path.join(PDF_DIR, 'convert.py')
    if not os.path.exists(convert_script):
        return False, 'convert.py غير موجود في outputs/pdf/'
    try:
        result = subprocess.run(
            [sys.executable, convert_script, card_path],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return False, result.stderr[:300] or result.stdout[:300]
        hp = html_path(card_path)
        pp = pdf_path(card_path)
        if not os.path.exists(hp):
            return False, f'HTML لم يُنشأ: {hp}'
        if not os.path.exists(pp):
            return False, f'PDF لم يُنشأ: {pp}'
        return True, f'HTML: {os.path.basename(hp)} | PDF: {os.path.basename(pp)}'
    except subprocess.TimeoutExpired:
        return False, 'انتهت مهلة التوليد (120 ثانية)'
    except Exception as e:
        return False, str(e)


# ── خطوة: فحص الجودة C1-C23 ─────────────────────────────────────────────────

def step_quality(card_path):
    """يشغّل بوابة الجودة الكاملة C1-C23."""
    if not _QG_AVAILABLE:
        return False, 'quality_gate.py غير متاح', []
    results, title_paren = run_checks(card_path)
    failed = [r for r in results if r[2] == 'FAIL']
    manual = [r for r in results if r[2] == 'MANUAL']
    passed = [r for r in results if r[2] == 'PASS']
    total = len(results)
    ok = len(failed) == 0
    detail = f'✅ {len(passed)}/{total}'
    if failed:
        detail += ' | ❌ ' + ' | '.join(f'[{r[0]}] {r[1]}' for r in failed[:5])
    if manual:
        detail += f' | ⚠️ {len(manual)} يدوي'
    return ok, detail, results


# ── خطوة: تحقق evidence ────────────────────────────────────────────────────────

def step_evidence(card_path):
    ep = evidence_path(card_path)
    if os.path.exists(ep):
        return True, f'موجود: {os.path.relpath(ep, REPO_ROOT)}'
    return False, f'مفقود: {os.path.relpath(ep, REPO_ROOT)}'


# ── خطوة: تحقق HTML/PDF موجودان ─────────────────────────────────────────────

def step_artifacts(card_path):
    hp = html_path(card_path)
    pp = pdf_path(card_path)
    missing = []
    if not os.path.exists(hp):
        missing.append('HTML')
    if not os.path.exists(pp):
        missing.append('PDF')
    if missing:
        return False, f'مفقود: {", ".join(missing)} — شغّل مع --build أولًا'
    return True, f'HTML ✅ | PDF ✅'


# ── خطوة: PDF LINK VALIDATION LOCK v1.0 ────────────────────────────────────

def step_pdf_links(card_path):
    """يفحص روابط PDF annotation مباشرة — PDF LINK VALIDATION LOCK v1.0."""
    if not _VPL_AVAILABLE:
        return False, 'validate_pdf_links.py غير متاح'
    pp = pdf_path(card_path)
    if not os.path.exists(pp):
        return False, f'PDF غير موجود — شغّل مع --build أولًا'
    results = validate_pdf_links([pp], verbose=False)
    n_pass = len(results['pass_open'])
    n_fail = len(results['fail_open'])
    total = n_pass + n_fail
    if n_fail > 0:
        fail_urls = ' | '.join(e['url'] for e in results['fail_open'][:3])
        return False, f'FAIL_OPEN={n_fail}/{total} — {fail_urls}'
    return True, f'PASS_OPEN={n_pass}/{total} — صفر FAIL_OPEN'


# ── خطوة: تحقق git نظيف ──────────────────────────────────────────────────────

def step_git_clean():
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        dirty = result.stdout.strip()
        if dirty:
            lines = dirty.split('\n')
            return False, f'{len(lines)} ملف غير مُودَع: {lines[0]}'
        return True, 'git نظيف'
    except Exception as e:
        return False, str(e)


# ── خطوة: تحقق scope guard ───────────────────────────────────────────────────

def step_scope(card_path, allowed=None):
    lock = find_lock(card_path)
    if not os.path.exists(lock):
        return True, 'لا يوجد lock — بطاقة جديدة أو غير مقفلة (PASS)'
    if not _SG_AVAILABLE:
        return False, 'scope_guard.py غير متاح'
    scope_results = run_scope_check(card_path, lock, allowed_elements=allowed)
    failed = [r for r in scope_results if r[2] == 'FAIL']
    if failed:
        detail = ' | '.join(f'[{r[0]}] {r[3]}' for r in failed)
        return False, detail
    return True, f'{len(scope_results)} فحوصات scope — PASS'


# ── تقرير Pipeline ────────────────────────────────────────────────────────────

def print_pipeline_report(card_path, steps):
    """
    steps: list of (label, ok, detail)
    """
    stem = os.path.basename(card_path)
    overall = all(ok for _, ok, _ in steps)
    print('=' * 65)
    print(f'  Pipeline — {stem}')
    print('=' * 65)
    for label, ok, detail in steps:
        icon = '✅' if ok else '❌'
        print(f'  {icon} {label}')
        if detail:
            print(f'       → {detail}')
    print('-' * 65)
    status = '✅ PASS' if overall else '❌ FAIL'
    print(f'  النتيجة النهائية: {status}')
    print('=' * 65)
    return overall


def run_pipeline(card_path, build=False, allowed=None, release=False):
    steps = []

    # 1. تحقق وجود artifacts (HTML/PDF)
    if build:
        ok, detail = step_build(card_path)
        steps.append(('توليد HTML/PDF', ok, detail))
        if not ok:
            print_pipeline_report(card_path, steps)
            return False
    else:
        ok, detail = step_artifacts(card_path)
        steps.append(('HTML/PDF موجودان', ok, detail))

    # 2. بوابة الجودة C1-C23
    ok, detail, _ = step_quality(card_path)
    steps.append(('بوابة الجودة C1–C23', ok, detail))

    # 3. Evidence
    ok, detail = step_evidence(card_path)
    steps.append(('ملف evidence', ok, detail))

    # 4. Scope Guard
    ok, detail = step_scope(card_path, allowed)
    steps.append(('Scope Guard', ok, detail))

    # 5. PDF LINK VALIDATION LOCK v1.0
    ok, detail = step_pdf_links(card_path)
    steps.append(('PDF Link Validation Lock v1.0', ok, detail))
    if not ok:
        print_pipeline_report(card_path, steps)
        return False

    # 6. Git نظيف (للـ release فقط)
    if release:
        ok, detail = step_git_clean()
        steps.append(('git نظيف', ok, detail))

    return print_pipeline_report(card_path, steps)


def load_manifest_status(card_path):
    """
    يقرأ حالة البطاقة من manifest إن وجد.
    القيم: active | locked | legacy_pre_contract | draft | None (لا manifest)
    """
    try:
        import yaml  # اختياري
    except ImportError:
        yaml = None

    stem = os.path.splitext(os.path.basename(card_path))[0]
    m = re.match(r'test_card_(\d+)', stem)
    candidates = []
    if m:
        candidates.append(os.path.join(MANIFESTS_DIR, f'test_card_{m.group(1)}.yaml'))
    candidates.append(os.path.join(MANIFESTS_DIR, f'{stem}.yaml'))

    for mpath in candidates:
        if not os.path.exists(mpath):
            continue
        # قراءة بسيطة بدون yaml لتجنب التبعية
        with open(mpath, encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('status:'):
                    val = line.split(':', 1)[1].strip().strip('"\'')
                    return val
    return None  # لا manifest


def run_validate_all():
    """
    يشغّل بوابة الجودة فقط على البطاقات ذات الحالة active/locked في manifests/.
    البطاقات legacy_pre_contract و draft تُعرض كـ SKIPPED ولا تكسر البناء.
    البطاقات بلا manifest تُعرض كـ SKIPPED.
    """
    manifests = sorted(glob.glob(os.path.join(MANIFESTS_DIR, '*.yaml')))

    if not manifests:
        print('⚠️  لا توجد manifests — أضف بطاقات إلى cards_manifest/')
        return True

    enforced = []   # active | locked
    skipped = []    # legacy_pre_contract | draft | no manifest

    for mpath in manifests:
        # استخرج مسار البطاقة من الـ manifest
        card_file = None
        status = None
        with open(mpath, encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('card_file:'):
                    card_file = line.split(':', 1)[1].strip().strip('"\'')
                if line.strip().startswith('status:'):
                    status = line.split(':', 1)[1].strip().strip('"\'')
        if card_file:
            abs_path = os.path.join(REPO_ROOT, card_file)
            if os.path.exists(abs_path):
                if status in ('active', 'locked'):
                    enforced.append((abs_path, status))
                else:
                    skipped.append((abs_path, status or 'غير محدد'))
            else:
                skipped.append((card_file, f'{status} — الملف غير موجود'))

    total = len(enforced) + len(skipped)
    print(f'\n🔍 Manifests: {total} | مفحوصة: {len(enforced)} | متخطاة: {len(skipped)}\n')

    all_pass = True
    for card_path, status in enforced:
        ok, detail, _ = step_quality(card_path)
        icon = '✅' if ok else '❌'
        print(f'  {icon} [{status}] {os.path.basename(card_path)}: {detail}')
        if not ok:
            all_pass = False

    for card_path, status in skipped:
        name = os.path.basename(card_path) if os.path.exists(str(card_path)) else card_path
        print(f'  ⏭  [SKIPPED — {status}] {name}')

    print()
    if all_pass:
        print('✅ جميع البطاقات النشطة/المقفلة PASS')
    else:
        print('❌ توجد بطاقات نشطة/مقفلة بها أخطاء')
    return all_pass


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='One-Click Card Pipeline')
    parser.add_argument('--card', help='مسار البطاقة أو رقمها (مثل: 009)')
    parser.add_argument('--build', action='store_true', help='ولّد HTML/PDF قبل الفحص')
    parser.add_argument('--release', action='store_true', help='وضع الإصدار — يتطلب git نظيف')
    parser.add_argument('--allow', action='append', dest='allowed',
                        help='عنصر مسموح بتعديله (يُكرر للعناصر المتعددة)')
    parser.add_argument('--validate-all', action='store_true',
                        help='فحص جميع البطاقات في outputs/')
    parser.add_argument('--lock', help='أنشئ scope lock للبطاقة بعد الاعتماد')

    args = parser.parse_args()

    if args.validate_all:
        ok = run_validate_all()
        sys.exit(0 if ok else 1)

    if args.lock:
        card_path = find_card_path(args.lock)
        if not card_path:
            print(f'❌ لم يُعثر على البطاقة: {args.lock}')
            sys.exit(1)
        # استدعاء scope_guard مباشرة لإنشاء القفل
        stem = os.path.splitext(os.path.basename(card_path))[0]
        lock_out = os.path.join(LOCKS_DIR, f'{stem}_scope_lock.json')
        os.makedirs(LOCKS_DIR, exist_ok=True)
        result = subprocess.run(
            [sys.executable, os.path.join(_scripts_dir, 'scope_guard.py'),
             '--card', card_path, '--generate-lock', '--output', lock_out],
            capture_output=True, text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            sys.exit(1)
        print(f'✅ Lock: {os.path.relpath(lock_out, REPO_ROOT)}')
        sys.exit(0)

    if not args.card:
        parser.print_help()
        sys.exit(1)

    card_path = find_card_path(args.card)
    if not card_path:
        print(f'❌ لم يُعثر على البطاقة: {args.card}')
        sys.exit(1)

    ok = run_pipeline(card_path, build=args.build,
                      allowed=args.allowed, release=args.release)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
