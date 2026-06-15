#!/usr/bin/env python3
"""
LINK SELECTION & VERIFICATION PROTOCOL v1.0
============================================
يفحص الروابط الحرجة في ملفات Markdown مقابل verified_link_registry.json.

يُستخدم في مرحلتين:
  1. قبل توليد PDF: تحقق أن كل رابط حرج موجود في السجل وبدرجة HIGH_VERIFIED.
  2. بعد توليد PDF: تحقق أن الروابط المستخرجة من PDF مطابقة للسجل.

القواعد:
  - كل رابط في (برامج التأهيل / الشهادات / الدورات) يجب أن يكون HIGH_VERIFIED في السجل.
  - أي رابط MEDIUM_VERIFIED أو مجهول يُوقف Pipeline ويمنع commit.
  - أي رابط من _not_verified يُوقف Pipeline فورًا.
  - لا استثناءات.

الاستخدام:
  python scripts/check_critical_links.py data/test_card_015_*.md
  python scripts/check_critical_links.py --pre-pdf data/test_card_015_*.md
"""

import argparse
import json
import re
import sys
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent / 'references' / 'verified_link_registry.json'

CRITICAL_SECTIONS = frozenset({
    'برامج التأهيل المعتمدة',
    'الشهادات المهنية الاحترافية',
    'الدورات الداعمة',
})

NON_CRITICAL_MARKERS = [
    'جهات التوظيف', 'المسار الوظيفي', 'الملاحظات', 'النصائح',
    'المهارات', 'الخبرات', 'المهام', 'طبيعة العمل', 'المرتبة',
    'المزايا', 'الشروط', 'متطلبات', 'التصنيف', 'المسميات',
]

URL_RE = re.compile(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)')


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        print(f'  ❌ FATAL: السجل غير موجود: {REGISTRY_PATH}')
        print('  يجب إنشاء references/verified_link_registry.json أولًا.')
        sys.exit(2)
    with open(REGISTRY_PATH, encoding='utf-8') as f:
        return json.load(f)


def build_lookup(registry: dict) -> tuple[dict, set]:
    """يبني index للروابط المؤكدة والمرفوضة."""
    verified = {}
    not_verified = set()
    for entry in registry.get('entries', []):
        verified[entry['url'].rstrip('/')] = entry
    for entry in registry.get('_not_verified', []):
        not_verified.add(entry['url'].rstrip('/'))
    return verified, not_verified


def extract_critical_links(md_path: str) -> list[dict]:
    """يستخرج الروابط من الأقسام الحرجة فقط."""
    links = []
    section = None
    in_critical = False
    with open(md_path, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            stripped = line.strip()
            if stripped in CRITICAL_SECTIONS:
                section = stripped
                in_critical = True
                continue
            is_non_crit = any(m in stripped for m in NON_CRITICAL_MARKERS)
            if is_non_crit and stripped not in CRITICAL_SECTIONS and not stripped.startswith('*'):
                in_critical = False
                section = stripped

            if in_critical:
                for text, url in URL_RE.findall(line):
                    links.append({
                        'file': md_path,
                        'line': lineno,
                        'section': section,
                        'text': text,
                        'url': url,
                    })
    return links


def classify_link(link: dict, verified: dict, not_verified: set) -> dict:
    """يصنّف الرابط: HIGH_VERIFIED / MEDIUM_VERIFIED / NOT_VERIFIED / UNKNOWN."""
    url = link['url'].rstrip('/')
    if url in not_verified:
        return {**link, 'verdict': 'NOT_VERIFIED', 'reason': 'موجود في قائمة _not_verified (فاشل مؤكد)'}
    if url in verified:
        entry = verified[url]
        v = entry.get('verification', 'UNKNOWN')
        return {**link, 'verdict': v, 'entry': entry,
                'reason': entry.get('evidence', '—')}
    return {**link, 'verdict': 'UNKNOWN',
            'reason': 'غير موجود في السجل — يجب إضافته وتحقيقه قبل الاستخدام'}


def check_md_files(md_paths: list[str], verbose: bool = False) -> tuple[list, list]:
    """
    يفحص ملفات Markdown.
    يُعيد (passed, failed) حيث failed = كل ما ليس HIGH_VERIFIED.
    """
    registry = load_registry()
    verified, not_verified = build_lookup(registry)

    passed = []
    failed = []

    for md_path in md_paths:
        links = extract_critical_links(md_path)
        for link in links:
            result = classify_link(link, verified, not_verified)
            if result['verdict'] == 'HIGH_VERIFIED':
                passed.append(result)
            else:
                failed.append(result)

    return passed, failed


def print_report(passed: list, failed: list, verbose: bool = False):
    print('=' * 60)
    print('  LINK SELECTION & VERIFICATION PROTOCOL v1.0')
    print('  فحص الروابط الحرجة مقابل verified_link_registry')
    print('=' * 60)

    if verbose or True:
        for r in passed:
            print(f'  ✅ HIGH_VERIFIED | {r["section"]} | {r["text"][:40]}')
            if verbose:
                print(f'     URL: {r["url"]}')

    if failed:
        print(f'\n  ❌ روابط مرفوضة ({len(failed)}):')
        for r in failed:
            print(f'\n  ❌ {r["verdict"]} | {r["section"]}')
            print(f'     النص: {r["text"]}')
            print(f'     URL : {r["url"]}')
            print(f'     السبب: {r["reason"]}')
            if r["verdict"] == "MEDIUM_VERIFIED":
                restr = r.get("entry", {}).get("restrictions", "")
                if restr:
                    print(f'     القيود: {restr}')

    print(f'\n  الإجمالي الحرج: {len(passed) + len(failed)}')
    print(f'  HIGH_VERIFIED  : {len(passed)}')
    print(f'  مرفوض          : {len(failed)}')

    if failed:
        n_not = sum(1 for r in failed if r['verdict'] == 'NOT_VERIFIED')
        n_med = sum(1 for r in failed if r['verdict'] == 'MEDIUM_VERIFIED')
        n_unk = sum(1 for r in failed if r['verdict'] == 'UNKNOWN')
        if n_not:
            print(f'    NOT_VERIFIED (فاشل مؤكد)  : {n_not}')
        if n_med:
            print(f'    MEDIUM_VERIFIED (غير كافٍ) : {n_med}')
        if n_unk:
            print(f'    UNKNOWN (غير مسجل)        : {n_unk}')
        print('\n  النتيجة: FAIL — ممنوع توليد PDF أو commit')
        print('  الإجراء: أضف روابط HIGH_VERIFIED للسجل أو غيّر البرنامج/الدورة/الشهادة')
        print('=' * 60)
        return False
    else:
        print('\n  النتيجة: PASS — جميع الروابط الحرجة HIGH_VERIFIED')
        print('=' * 60)
        return True


def main():
    parser = argparse.ArgumentParser(
        description='LINK SELECTION & VERIFICATION PROTOCOL v1.0'
    )
    parser.add_argument('files', nargs='+', help='ملفات Markdown للفحص')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--pre-pdf', action='store_true',
                        help='وضع ما قبل PDF — يوقف العملية عند أي فشل')
    args = parser.parse_args()

    passed, failed = check_md_files(args.files, verbose=args.verbose)
    ok = print_report(passed, failed, verbose=args.verbose)

    if not ok:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
