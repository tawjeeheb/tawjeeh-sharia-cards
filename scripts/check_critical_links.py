#!/usr/bin/env python3
"""
LINK SELECTION & VERIFICATION PROTOCOL v2.0
============================================
يفحص الروابط الحرجة في ملفات Markdown مقابل verified_link_registry.json.
مدعوم بـ SMART LINK RESOLUTION ENGINE v1.0:
  - إذا الرابط موجود في السجل بـ HIGH_VERIFIED → قبول مباشر
  - إذا الرابط UNKNOWN → يُرجع NEEDS_RESOLUTION (يحتاج WebSearch من Claude)
  - إذا فشل التحقق → يُرفض

الاستخدام:
  python scripts/check_critical_links.py data/test_card_015_*.md
  python scripts/check_critical_links.py --list-unresolved data/test_card_015_*.md
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
    """
    يصنّف الرابط مقابل السجل + LINK TYPE BOUNDARY LOCK v1.0.

    النتائج الممكنة:
      HIGH_VERIFIED / MEDIUM_VERIFIED / NOT_VERIFIED / NEEDS_RESOLUTION
      TYPE_MISMATCH / COURSE_PLATFORM_NOT_ALLOWED / UNKNOWN_TYPE
    """
    from smart_link_resolver import (
        is_bare_homepage, is_login_required, check_type_boundary,
    )

    url = link['url'].rstrip('/')

    # فحص أولي سريع (قبل الرجوع للسجل)
    if is_bare_homepage(link['url']):
        return {**link, 'verdict': 'NOT_VERIFIED',
                'reason': 'صفحة رئيسية عامة — مسار غير محدد (bare homepage)'}
    if is_login_required(link['url']):
        return {**link, 'verdict': 'NOT_VERIFIED',
                'reason': 'KNOWN_LOGIN_REQUIRED — يتطلب تسجيل دخول'}

    if url in not_verified:
        return {**link, 'verdict': 'NOT_VERIFIED', 'reason': 'موجود في قائمة _not_verified (فاشل مؤكد)'}

    if url in verified:
        entry = verified[url]
        v = entry.get('verification', 'UNKNOWN')

        if v == 'HIGH_VERIFIED':
            # ── LINK TYPE BOUNDARY LOCK v1.0 ─────────────────────────────
            registry_type = entry.get('type', '')
            boundary = check_type_boundary(link['url'], link['section'], registry_type)
            if boundary['verdict'] != 'TYPE_OK':
                return {**link,
                        'verdict': boundary['verdict'],
                        'entry': entry,
                        'reason': boundary['reason']}
            # ─────────────────────────────────────────────────────────────
            return {**link, 'verdict': 'HIGH_VERIFIED', 'entry': entry,
                    'reason': entry.get('evidence', '—')}

        return {**link, 'verdict': v, 'entry': entry,
                'reason': entry.get('evidence', '—')}

    # UNKNOWN — يحتاج SMART LINK RESOLUTION ENGINE
    return {**link, 'verdict': 'NEEDS_RESOLUTION',
            'reason': (
                'غير موجود في السجل — يحتاج WebSearch للاكتشاف التلقائي. '
                'شغّل: python scripts/smart_link_resolver.py resolve '
                f'--url "{link["url"]}" --name "{link["text"]}" '
                '--section program --title "<title>" --snippet "<snippet>"'
            )}


TYPE_BOUNDARY_VERDICTS = frozenset({
    'TYPE_MISMATCH', 'COURSE_PLATFORM_NOT_ALLOWED', 'UNKNOWN_TYPE',
    'DUPLICATE_ENTITY_ACROSS_SECTIONS', 'CONTENT_TYPE_REWRITE_ATTEMPT',
})


def detect_duplicates(links: list[dict]) -> list[dict]:
    """
    LINK TYPE BOUNDARY LOCK v1.0 — كشف التكرار عبر الأقسام.
    يكتشف نفس الرابط موجودًا في أكثر من قسم حرج.
    """
    from collections import defaultdict
    url_sections: dict[str, list] = defaultdict(list)
    for link in links:
        url_sections[link['url'].rstrip('/')].append(link)

    duplicates = []
    for url, occurrences in url_sections.items():
        sections = list({o['section'] for o in occurrences})
        if len(sections) > 1:
            for occ in occurrences:
                duplicates.append({
                    **occ,
                    'verdict': 'DUPLICATE_ENTITY_ACROSS_SECTIONS',
                    'reason': (
                        f'نفس الرابط موجود في {len(sections)} أقسام: '
                        + ' و '.join(f'[{s}]' for s in sections)
                    ),
                })
    return duplicates


def check_md_files(
    md_paths: list[str],
    verbose: bool = False,
    list_unresolved: bool = False,
) -> tuple[list, list, list]:
    """
    يفحص ملفات Markdown مقابل السجل + LINK TYPE BOUNDARY LOCK v1.0.
    يُعيد (passed, failed, needs_resolution).

    passed          : HIGH_VERIFIED + TYPE_OK
    failed          : NOT_VERIFIED / MEDIUM_VERIFIED / TYPE_MISMATCH /
                      COURSE_PLATFORM_NOT_ALLOWED / DUPLICATE_ENTITY_ACROSS_SECTIONS
    needs_resolution: روابط UNKNOWN تحتاج SMART LINK RESOLUTION ENGINE
    """
    registry = load_registry()
    verified, not_verified = build_lookup(registry)

    passed = []
    failed = []
    needs_resolution = []

    for md_path in md_paths:
        links = extract_critical_links(md_path)

        # فحص التكرار عبر الأقسام
        dup_results = detect_duplicates(links)
        dup_urls = {r['url'].rstrip('/') for r in dup_results}

        for link in links:
            result = classify_link(link, verified, not_verified)
            url_norm = link['url'].rstrip('/')

            # إذا الرابط مكرر عبر أقسام: اعرض DUPLICATE + TYPE_MISMATCH معاً إن وُجدا
            if url_norm in dup_urls:
                dup = next(
                    (d for d in dup_results
                     if d['url'].rstrip('/') == url_norm
                     and d['line'] == link['line']),
                    None,
                )
                if dup:
                    # أضف حكم DUPLICATE دائماً
                    failed.append(dup)
                    # إذا classify كشف أيضًا TYPE_MISMATCH أو COURSE_PLATFORM_NOT_ALLOWED → أضفه كحكم مستقل
                    if result['verdict'] in TYPE_BOUNDARY_VERDICTS and result['verdict'] != 'DUPLICATE_ENTITY_ACROSS_SECTIONS':
                        failed.append({**result, 'verdict': result['verdict'],
                                        'reason': f'[مستقل] {result["reason"]}'})
                    continue

            if result['verdict'] == 'HIGH_VERIFIED':
                passed.append(result)
            elif result['verdict'] == 'NEEDS_RESOLUTION':
                needs_resolution.append(result)
            else:
                failed.append(result)

    return passed, failed, needs_resolution


def print_report(passed: list, failed: list, verbose: bool = False,
                 needs_resolution: list = None):
    needs_resolution = needs_resolution or []
    print('=' * 60)
    print('  LINK SELECTION & VERIFICATION PROTOCOL v2.0')
    print('  + SMART LINK RESOLUTION ENGINE')
    print('  + LINK TYPE BOUNDARY LOCK v1.0')
    print('  فحص الروابط الحرجة مقابل verified_link_registry')
    print('=' * 60)

    if verbose or True:
        for r in passed:
            print(f'  ✅ HIGH_VERIFIED | {r["section"]} | {r["text"][:40]}')
            if verbose:
                print(f'     URL: {r["url"]}')

    if needs_resolution:
        print(f'\n  🔍 روابط تحتاج SMART LINK RESOLUTION ({len(needs_resolution)}):')
        for r in needs_resolution:
            print(f'\n  🔍 NEEDS_RESOLUTION | {r["section"]}')
            print(f'     النص: {r["text"]}')
            print(f'     URL : {r["url"]}')
            print(f'     الإجراء: سيُشغَّل SMART LINK RESOLUTION ENGINE تلقائيًا')

    if failed:
        type_fails = [r for r in failed if r['verdict'] in TYPE_BOUNDARY_VERDICTS]
        other_fails = [r for r in failed if r['verdict'] not in TYPE_BOUNDARY_VERDICTS]

        if type_fails:
            print(f'\n  🔒 LINK TYPE BOUNDARY LOCK — انتهاكات ({len(type_fails)}):')
            for r in type_fails:
                print(f'\n  🔒 {r["verdict"]} | {r["section"]}')
                print(f'     النص: {r["text"]}')
                print(f'     URL : {r["url"]}')
                print(f'     السبب: {r["reason"]}')

        if other_fails:
            print(f'\n  ❌ روابط مرفوضة ({len(other_fails)}):')
            for r in other_fails:
                print(f'\n  ❌ {r["verdict"]} | {r["section"]}')
                print(f'     النص: {r["text"]}')
                print(f'     URL : {r["url"]}')
                print(f'     السبب: {r["reason"]}')
                if r["verdict"] == "MEDIUM_VERIFIED":
                    restr = r.get("entry", {}).get("restrictions", "")
                    if restr:
                        print(f'     القيود: {restr}')

    total = len(passed) + len(failed) + len(needs_resolution)
    print(f'\n  الإجمالي الحرج: {total}')
    print(f'  HIGH_VERIFIED    : {len(passed)}')
    print(f'  مرفوض            : {len(failed)}')
    print(f'  يحتاج اكتشاف    : {len(needs_resolution)}')

    if failed or needs_resolution:
        if failed:
            n_not = sum(1 for r in failed if r['verdict'] == 'NOT_VERIFIED')
            n_med = sum(1 for r in failed if r['verdict'] == 'MEDIUM_VERIFIED')
            if n_not:
                print(f'    NOT_VERIFIED (فاشل مؤكد)  : {n_not}')
            if n_med:
                print(f'    MEDIUM_VERIFIED (غير كافٍ) : {n_med}')
        if needs_resolution:
            print(f'    NEEDS_RESOLUTION (يحتاج WebSearch): {len(needs_resolution)}')
        if failed:
            print('\n  النتيجة: FAIL — ممنوع توليد PDF أو commit')
            print('  الإجراء: شغّل SMART LINK RESOLUTION ENGINE أو غيّر المحتوى')
        else:
            print('\n  النتيجة: PENDING_RESOLUTION — ينتظر اكتشاف الروابط')
            print('  الإجراء: شغّل smart_link_resolver.py resolve لكل رابط')
        print('=' * 60)
        return False
    else:
        print('\n  النتيجة: PASS — جميع الروابط الحرجة HIGH_VERIFIED')
        print('=' * 60)
        return True


def main():
    parser = argparse.ArgumentParser(
        description='LINK SELECTION & VERIFICATION PROTOCOL v2.0'
    )
    parser.add_argument('files', nargs='+', help='ملفات Markdown للفحص')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--list-unresolved', action='store_true',
                        help='اعرض فقط الروابط التي تحتاج اكتشافًا (لـ pipeline)')
    parser.add_argument('--pre-pdf', action='store_true',
                        help='وضع ما قبل PDF — يوقف العملية عند أي فشل')
    args = parser.parse_args()

    passed, failed, needs_res = check_md_files(args.files, verbose=args.verbose)

    if args.list_unresolved:
        # إخراج JSON للـ pipeline
        import json
        print(json.dumps([r['url'] for r in needs_res], ensure_ascii=False))
        sys.exit(0 if not needs_res else 2)

    ok = print_report(passed, failed, verbose=args.verbose, needs_resolution=needs_res)

    if not ok:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
