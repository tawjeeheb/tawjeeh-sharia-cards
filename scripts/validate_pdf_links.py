#!/usr/bin/env python3
"""
PDF LINK VALIDATION LOCK v1.1
==============================
يستخرج الروابط من PDF annotation مباشرة ويفحصها عبر HTTP.
الفحص من PDF نفسه — لا من Markdown ولا من HTML.

الحالات (وضع عادي):
  PASS_OPEN    — HTTP ≠ 000 (الخادم يستجيب، حتى لو 403 بسبب IP)
  REPLACED_OPEN — كان FAIL_OPEN وتم استبداله تلقائيًا (للتقارير فقط)
  FAIL_OPEN    — HTTP = 000 (النطاق غير موجود أو لا استجابة)

الحالات الإضافية في وضع --user-open-strict:
  PASS_OFFICIAL_SPECIFIC — يستجيب الخادم (كل ما لا يقع في فئة أخرى)
  FAIL_USER_OPEN  — HTTP = 000 أو 404 أو URL يطابق KNOWN_LOGIN_REQUIRED
  WARN_GENERAL_PAGE — URL صفحة رئيسية بلا مسار محدد (مقبول للتوظيف)

قاعدة صارمة: FAIL_OPEN > 0 أو FAIL_USER_OPEN > 0 → فشل إلزامي، لا اعتماد.
"""

import argparse
import re
import subprocess
import sys
from pypdf import PdfReader

# ── أنماط تستلزم تسجيل دخول (لا يمكن للقارئ فتحها مباشرة) ──────────────────
KNOWN_LOGIN_REQUIRED = [
    re.compile(r'lms\.doroob\.sa/courses/'),
    re.compile(r'fa\.gov\.sa/Services/ProgramDetails/'),
]

# ── أنماط الصفحات الرئيسية العامة (بلا مسار محدد) ──────────────────────────
_BARE_HOMEPAGE = re.compile(r'^https?://[^/]+(/[a-zA-Z]{0,3})?/?$')

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


def validate_pdf_links(pdf_paths: list[str], verbose: bool = False, strict: bool = False) -> dict:
    """
    يفحص كل روابط PDF المُعطاة.

    strict=False (وضع عادي):
      يُعيد dict يحتوي: pass_open, fail_open, details

    strict=True (وضع --user-open-strict):
      يُعيد dict يحتوي: pass_official_specific, fail_user_open, warn_general_page, details
      - 000 → FAIL_USER_OPEN
      - 404 → FAIL_USER_OPEN
      - KNOWN_LOGIN_REQUIRED → FAIL_USER_OPEN
      - BARE_HOMEPAGE → WARN_GENERAL_PAGE
      - غير ذلك (بما في ذلك 403) → PASS_OFFICIAL_SPECIFIC
    """
    all_links = {}
    for pdf_path in pdf_paths:
        for url in extract_pdf_links(pdf_path):
            if url not in all_links:
                all_links[url] = pdf_path

    if strict:
        results = {'pass_official_specific': [], 'fail_user_open': [], 'warn_general_page': [], 'details': []}
    else:
        results = {'pass_open': [], 'fail_open': [], 'details': []}

    for url, source in sorted(all_links.items()):
        integrity_issues = validate_url_integrity(url)
        http_code = check_url(url)

        if strict:
            is_login_required = any(p.search(url) for p in KNOWN_LOGIN_REQUIRED)
            is_bare_homepage = bool(_BARE_HOMEPAGE.match(url))
            is_fail = (http_code in ('000', '404')) or bool(integrity_issues) or is_login_required

            if is_fail:
                status = 'FAIL_USER_OPEN'
            elif is_bare_homepage:
                status = 'WARN_GENERAL_PAGE'
            else:
                status = 'PASS_OFFICIAL_SPECIFIC'

            entry = {
                'url': url,
                'source': source,
                'http_code': http_code,
                'integrity_issues': integrity_issues,
                'status': status,
            }
            results['details'].append(entry)
            if status == 'FAIL_USER_OPEN':
                results['fail_user_open'].append(entry)
            elif status == 'WARN_GENERAL_PAGE':
                results['warn_general_page'].append(entry)
            else:
                results['pass_official_specific'].append(entry)

            if verbose or status == 'FAIL_USER_OPEN':
                mark = '✅' if status == 'PASS_OFFICIAL_SPECIFIC' else ('⚠️' if status == 'WARN_GENERAL_PAGE' else '❌')
                issues_str = f' [{", ".join(integrity_issues)}]' if integrity_issues else ''
                print(f'  {mark} {status} [{http_code}]{issues_str} {url}')
        else:
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
    parser.add_argument('--user-open-strict', action='store_true',
                        help='وضع صارم: 000/404/login-required → FAIL_USER_OPEN، homepage → WARN_GENERAL_PAGE')
    args = parser.parse_args()

    print('=' * 60)
    print('  PDF LINK VALIDATION LOCK v1.1')
    if args.user_open_strict:
        print('  وضع: USER_OPEN_STRICT')
    print('=' * 60)

    results = validate_pdf_links(args.pdfs, verbose=args.verbose, strict=args.user_open_strict)

    total = len(results['details'])

    if args.user_open_strict:
        n_pass = len(results['pass_official_specific'])
        n_warn = len(results['warn_general_page'])
        n_fail = len(results['fail_user_open'])

        print(f'\n  الإجمالي              : {total}')
        print(f'  PASS_OFFICIAL_SPECIFIC: {n_pass}')
        print(f'  WARN_GENERAL_PAGE     : {n_warn}')
        print(f'  FAIL_USER_OPEN        : {n_fail}')

        if n_warn > 0:
            print('\n  ⚠️ صفحات رئيسية عامة (مقبولة لأقسام التوظيف):')
            for e in results['warn_general_page']:
                print(f'     [{e["http_code"]}] {e["url"]}')

        if n_fail > 0:
            print('\n  ❌ روابط فاشلة (لا يمكن للقارئ فتحها):')
            for e in results['fail_user_open']:
                print(f'     [{e["http_code"]}] {e["url"]}')
            print('\n  النتيجة: FAIL — لا يُعتمد هذا PDF')
            print('=' * 60)
            sys.exit(1)
        else:
            print('\n  النتيجة: PASS — لا FAIL_USER_OPEN')
            print('=' * 60)
            sys.exit(0)
    else:
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
