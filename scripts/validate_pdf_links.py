#!/usr/bin/env python3
"""
PDF LINK VALIDATION LOCK v1.0
==============================
يستخرج الروابط من PDF annotation مباشرة ويفحصها عبر HTTP.
الفحص من PDF نفسه — لا من Markdown ولا من HTML.

الحالات المقبولة:
  PASS_OPEN    — HTTP ≠ 000 (الخادم يستجيب، حتى لو 403 بسبب IP)
  REPLACED_OPEN — كان FAIL_OPEN وتم استبداله تلقائيًا (للتقارير فقط)
  FAIL_OPEN    — HTTP = 000 (النطاق غير موجود أو لا استجابة)

قاعدة صارمة: FAIL_OPEN > 0 → فشل إلزامي، لا اعتماد.
"""

import argparse
import re
import subprocess
import sys
from pypdf import PdfReader

# ── روابط الفوتر الثابتة (مفحوصة ومعتمدة مسبقًا) ──────────────────────────
FOOTER_URLS = frozenset([
    'https://www.tiktok.com/@tawjeeh.hub',
    'https://instagram.com/tawjeeh.hub',
    'https://www.snapchat.com/add/tawjeeh.hub',
    'https://x.com/tawjeeh_hub',
    'https://www.youtube.com/@tawjeeh_hub',
    'https://www.tawjeeh.hub',
])

# ── محارف خفية يجب ألا تظهر في href ──────────────────────────────────────────
_INVISIBLE = re.compile(
    r'[​‌‍‎‏'
    r'‪‫‬‭‮'
    r'﻿­]'
)
_TRAILING = re.compile(r'[.,،؛;:!?)\]↗\s]+$')


def extract_pdf_links(pdf_path: str) -> list[str]:
    """استخراج كل روابط annotations من ملف PDF (باستثناء الفوتر)."""
    reader = PdfReader(pdf_path)
    seen = set()
    links = []
    for page in reader.pages:
        annots = page.get('/Annots')
        if not annots:
            continue
        for annot in annots:
            obj = annot.get_object()
            if obj.get('/Subtype') != '/Link':
                continue
            action = obj.get('/A')
            if not action:
                continue
            uri = action.get('/URI', '')
            if not uri or uri in FOOTER_URLS or uri in seen:
                continue
            seen.add(uri)
            links.append(uri)
    return links


def check_url(url: str, timeout: int = 8) -> str:
    """يُعيد HTTP status code أو '000' عند فشل الاتصال."""
    r = subprocess.run(
        ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
         '--max-time', str(timeout), '-L', '--connect-timeout', '5', url],
        capture_output=True, text=True
    )
    return r.stdout.strip() or '000'


def validate_url_integrity(url: str) -> list[str]:
    """يكشف محارف خفية أو trailing جunk في الرابط."""
    issues = []
    if _INVISIBLE.search(url):
        issues.append('invisible_unicode_char')
    if _TRAILING.search(url):
        issues.append(f'trailing_junk:{repr(url[-1])}')
    return issues


def validate_pdf_links(pdf_paths: list[str], verbose: bool = False) -> dict:
    """
    يفحص كل روابط PDF المُعطاة.
    يُعيد dict يحتوي: pass_open, fail_open, details
    """
    all_links = {}
    for pdf_path in pdf_paths:
        for url in extract_pdf_links(pdf_path):
            if url not in all_links:
                all_links[url] = pdf_path

    results = {'pass_open': [], 'fail_open': [], 'details': []}

    for url, source in sorted(all_links.items()):
        integrity_issues = validate_url_integrity(url)
        http_code = check_url(url)
        is_fail = (http_code == '000') or bool(integrity_issues)

        status = 'FAIL_OPEN' if is_fail else 'PASS_OPEN'
        entry = {
            'url': url,
            'source': source,
            'http_code': http_code,
            'integrity_issues': integrity_issues,
            'status': status,
        }
        results['details'].append(entry)
        if is_fail:
            results['fail_open'].append(entry)
        else:
            results['pass_open'].append(entry)

        if verbose or is_fail:
            mark = '✅' if not is_fail else '❌'
            issues_str = f' [{", ".join(integrity_issues)}]' if integrity_issues else ''
            print(f'  {mark} {status} [{http_code}]{issues_str} {url}')

    return results


def main():
    parser = argparse.ArgumentParser(
        description='PDF LINK VALIDATION LOCK v1.0 — فحص إلزامي لروابط PDF'
    )
    parser.add_argument('pdfs', nargs='+', help='ملفات PDF للفحص')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='اعرض كل الروابط لا FAIL فقط')
    parser.add_argument('--timeout', type=int, default=8,
                        help='مهلة الاتصال (ثواني)')
    args = parser.parse_args()

    print('=' * 60)
    print('  PDF LINK VALIDATION LOCK v1.0')
    print('=' * 60)

    results = validate_pdf_links(args.pdfs, verbose=args.verbose)

    total = len(results['details'])
    n_pass = len(results['pass_open'])
    n_fail = len(results['fail_open'])

    print(f'\n  الإجمالي : {total}')
    print(f'  PASS_OPEN: {n_pass}')
    print(f'  FAIL_OPEN: {n_fail}')

    if n_fail > 0:
        print('\n  ❌ روابط فاشلة:')
        for e in results['fail_open']:
            print(f'     [{e["http_code"]}] {e["url"]}')
        print('\n  النتيجة: FAIL — لا يُعتمد هذا PDF')
        print('=' * 60)
        sys.exit(1)
    else:
        print('\n  النتيجة: PASS — جميع الروابط صالحة')
        print('=' * 60)
        sys.exit(0)


if __name__ == '__main__':
    main()
