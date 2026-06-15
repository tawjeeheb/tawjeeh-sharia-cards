#!/usr/bin/env python3
"""
SMART LINK RESOLUTION ENGINE v1.0
===================================
يُحوّل verified_link_registry من whitelist مغلق إلى Cache ذكي.

المنطق:
  1. CACHE_HIT_HIGH   : الرابط موجود في السجل بـ HIGH_VERIFIED → قبول مباشر
  2. CACHE_HIT_BAD    : الرابط موجود بـ REJECTED/DEPRECATED/NOT_VERIFIED → رفض
  3. UNKNOWN          : الرابط غير موجود في السجل → تشغيل DISCOVERY_MODE
  4. DISCOVERY_MODE   : البحث عن الصفحة الرسمية وإضافتها للسجل تلقائيًا

حالات السجل:
  HIGH_VERIFIED      : مثبت، مسموح في البطاقات
  DISCOVERED_PENDING : عُثر عليه لكن لم يُضَف بعد (مؤقت أثناء المعالجة)
  REJECTED           : مرفوض مع سبب موثق
  DEPRECATED         : كان صحيحًا ثم انتهت صلاحيته
  NOT_VERIFIED       : غير مثبت أو فشل التحقق

ممنوع دخول PDF: DISCOVERED_PENDING / REJECTED / DEPRECATED / NOT_VERIFIED / UNKNOWN
"""

import json
import re
import sys
import os
import argparse
from datetime import date
from pathlib import Path
from typing import Optional

REGISTRY_PATH = Path(__file__).parent.parent / 'references' / 'verified_link_registry.json'

BARE_HOMEPAGE_RE = re.compile(
    r'^https?://[^/]+(/(ar|en|index\.html?|home|default\.aspx?|Pages/Default\.aspx?))?/?$',
    re.IGNORECASE,
)
LOGIN_PATTERNS = [
    'lms.doroob.sa/courses/',
    'fa.gov.sa/Services/ProgramDetails/',
]

SECTION_TYPES = {
    'programs':       'برامج التأهيل المعتمدة',
    'certifications': 'الشهادات المهنية الاحترافية',
    'courses':        'الدورات الداعمة',
}

RESOLUTION_STATES = {
    'CACHE_HIT_HIGH':   'رابط مثبت في السجل — قبول مباشر',
    'CACHE_HIT_BAD':    'رابط مرفوض في السجل — استبدال إلزامي',
    'DISCOVERED':       'رابط جديد — تم اكتشافه وإضافته للسجل',
    'UNRESOLVABLE':     'لم يُعثر على رابط صالح — يجب تغيير المحتوى',
}

# ── تحميل السجل ──────────────────────────────────────────────────────────────

def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {'entries': [], '_not_verified': []}
    with open(REGISTRY_PATH, encoding='utf-8') as f:
        return json.load(f)


def save_registry(reg: dict):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)


def build_lookup(reg: dict) -> tuple[dict, set]:
    """يبني فهرسًا سريعًا للروابط."""
    verified = {}
    rejected = set()
    for e in reg.get('entries', []):
        verified[e['url'].rstrip('/')] = e
    for e in reg.get('_not_verified', []):
        rejected.add(e['url'].rstrip('/'))
    return verified, rejected


# ── فحوصات أولية ─────────────────────────────────────────────────────────────

def is_bare_homepage(url: str) -> bool:
    return bool(BARE_HOMEPAGE_RE.match(url))


def is_login_required(url: str) -> bool:
    return any(p in url for p in LOGIN_PATTERNS)


def is_specific_page(url: str) -> bool:
    """يتحقق أن الرابط صفحة محددة وليس homepage."""
    if is_bare_homepage(url):
        return False
    if is_login_required(url):
        return False
    # المسار يجب أن يكون أطول من 3 أحرف بعد الدومين
    path = re.sub(r'^https?://[^/]+', '', url).strip('/')
    return len(path) > 3


# ── البحث النصي في نتائج WebSearch ──────────────────────────────────────────

def name_appears_in_results(name: str, search_snippet: str) -> bool:
    """يتحقق أن اسم البرنامج ظاهر في نتائج البحث (مطابقة جزئية)."""
    if not search_snippet or not name:
        return False
    # تحويل للحروف الصغيرة وإزالة علامات الترقيم
    name_tokens = set(re.findall(r'\w+', name.lower()))
    snippet_tokens = set(re.findall(r'\w+', search_snippet.lower()))
    # يكفي أن 50% من كلمات الاسم تظهر في المقتطف
    if not name_tokens:
        return False
    overlap = name_tokens & snippet_tokens
    return len(overlap) / len(name_tokens) >= 0.5


# ── واجهة إضافة رابط للسجل ──────────────────────────────────────────────────

def add_to_registry(
    url: str,
    name_ar: str,
    name_en: str,
    section_type: str,
    owner: str,
    evidence: str,
    verification: str = 'HIGH_VERIFIED',
    restrictions: Optional[str] = None,
) -> dict:
    """يُضيف رابطًا للسجل ويحفظه. يعيد الإدخال المُضاف."""
    reg = load_registry()
    verified, _ = build_lookup(reg)
    url_norm = url.rstrip('/')

    if url_norm in verified:
        existing = verified[url_norm]
        if existing.get('verification') == verification:
            return existing
        # تحديث إذا كان موجودًا بدرجة أقل
        for e in reg['entries']:
            if e['url'].rstrip('/') == url_norm:
                e['verification'] = verification
                e['evidence'] = evidence
                e['date'] = str(date.today())
                if restrictions:
                    e['restrictions'] = restrictions
                break
        save_registry(reg)
        return verified[url_norm]

    entry = {
        'url': url_norm,
        'name_ar': name_ar,
        'name_en': name_en or name_ar,
        'type': section_type,
        'owner': owner,
        'verification': verification,
        'date': str(date.today()),
        'evidence': evidence,
        'suitable_for': [section_type + 's'] if not section_type.endswith('s') else [section_type],
    }
    if restrictions:
        entry['restrictions'] = restrictions

    reg.setdefault('entries', []).append(entry)
    save_registry(reg)
    return entry


def add_rejection(url: str, reason: str, verdict: str = 'FAIL_VERIFIED'):
    """يُضيف رابطًا لقائمة المرفوضات."""
    reg = load_registry()
    url_norm = url.rstrip('/')
    rejected_urls = {e['url'].rstrip('/') for e in reg.get('_not_verified', [])}
    if url_norm not in rejected_urls:
        reg.setdefault('_not_verified', []).append({
            'url': url_norm,
            'reason': reason,
            'verdict': verdict,
            'date': str(date.today()),
        })
        save_registry(reg)


# ── نتيجة الحل ──────────────────────────────────────────────────────────────

class Resolution:
    def __init__(
        self,
        state: str,
        original_url: str,
        final_url: Optional[str],
        evidence: str,
        name: str,
        section_type: str,
    ):
        self.state = state
        self.original_url = original_url
        self.final_url = final_url
        self.evidence = evidence
        self.name = name
        self.section_type = section_type
        self.needs_content_change = (state == 'UNRESOLVABLE')
        self.ok = state in ('CACHE_HIT_HIGH', 'DISCOVERED')

    def to_dict(self) -> dict:
        return {
            'state': self.state,
            'original_url': self.original_url,
            'final_url': self.final_url,
            'evidence': self.evidence,
            'name': self.name,
            'section_type': self.section_type,
            'ok': self.ok,
            'needs_content_change': self.needs_content_change,
        }

    def __repr__(self):
        return f'Resolution({self.state}, {self.final_url})'


# ── المحرك الأساسي ──────────────────────────────────────────────────────────

class SmartLinkResolver:
    """
    SMART LINK RESOLUTION ENGINE v1.0

    الاستخدام:
      resolver = SmartLinkResolver()
      result = resolver.resolve(url, name, section_type)
      # section_type: 'program' | 'certification' | 'course'
    """

    def __init__(self):
        self.reg = load_registry()
        self.verified, self.rejected = build_lookup(self.reg)
        self._search_results_cache = {}  # url → search evidence

    def resolve(
        self,
        url: str,
        name: str,
        section_type: str,
        search_evidence: Optional[str] = None,
    ) -> Resolution:
        """
        الحل الكامل للرابط.

        search_evidence: نص مقتطف من WebSearch يُمرَّر من الخارج (من Claude).
                         إذا لم يُمرَّر، يُرجع NEEDS_WEBSEARCH.
        """
        url_norm = url.rstrip('/')

        # 1. فحص أولي: صفحات عامة
        if is_bare_homepage(url):
            return Resolution(
                'CACHE_HIT_BAD', url, None,
                'Bare homepage — مسار غير محدد',
                name, section_type,
            )

        # 2. فحص تسجيل الدخول
        if is_login_required(url):
            return Resolution(
                'CACHE_HIT_BAD', url, None,
                'KNOWN_LOGIN_REQUIRED',
                name, section_type,
            )

        # 3. فحص قائمة المرفوضات
        if url_norm in self.rejected:
            return Resolution(
                'CACHE_HIT_BAD', url, None,
                'موجود في _not_verified',
                name, section_type,
            )

        # 4. فحص السجل (Cache Hit)
        if url_norm in self.verified:
            entry = self.verified[url_norm]
            v = entry.get('verification', 'UNKNOWN')
            if v == 'HIGH_VERIFIED':
                return Resolution(
                    'CACHE_HIT_HIGH', url, url,
                    entry.get('evidence', '—'),
                    name, section_type,
                )
            elif v in ('REJECTED', 'DEPRECATED', 'NOT_VERIFIED'):
                return Resolution(
                    'CACHE_HIT_BAD', url, None,
                    f'{v}: {entry.get("evidence", "—")}',
                    name, section_type,
                )
            elif v == 'MEDIUM_VERIFIED':
                # MEDIUM يحتاج اكتشافًا للتحقق
                pass  # اسقط إلى مرحلة الاكتشاف

        # 5. DISCOVERY_MODE — يحتاج search_evidence من WebSearch
        if search_evidence is None:
            return Resolution(
                'NEEDS_WEBSEARCH', url, None,
                'يحتاج WebSearch — استخدم resolve_with_search()',
                name, section_type,
            )

        return self._discover(url, name, section_type, search_evidence)

    def resolve_with_search(
        self,
        url: str,
        name: str,
        section_type: str,
        search_title: str,
        search_snippet: str,
        owner: str = '',
    ) -> Resolution:
        """
        يُكمل الحل بعد تلقي نتائج WebSearch.

        search_title : عنوان الصفحة من WebSearch
        search_snippet: المقتطف النصي من WebSearch
        """
        url_norm = url.rstrip('/')
        combined = f'{search_title} {search_snippet}'

        # التحقق من المطابقة
        name_found = name_appears_in_results(name, combined)
        specific = is_specific_page(url)

        if specific and name_found:
            # إضافة للسجل كـ HIGH_VERIFIED
            entry = add_to_registry(
                url=url,
                name_ar=name,
                name_en=name,
                section_type=section_type,
                owner=owner or 'WebSearch Discovered',
                evidence=f'WebSearch CONFIRMED: {search_title[:100]}',
            )
            # تحديث الكاش المحلي
            self.verified[url_norm] = entry
            return Resolution(
                'DISCOVERED', url, url,
                f'WebSearch CONFIRMED — title: {search_title[:80]}',
                name, section_type,
            )

        reason = []
        if not specific:
            reason.append('صفحة عامة — مسار غير محدد')
        if not name_found:
            reason.append(f'اسم "{name[:40]}" لم يظهر في نتائج البحث')

        # إضافة للمرفوضات
        add_rejection(url, ' | '.join(reason), 'FAIL_VERIFIED')
        self.rejected.add(url_norm)
        return Resolution(
            'UNRESOLVABLE', url, None,
            ' | '.join(reason),
            name, section_type,
        )

    def _discover(self, url, name, section_type, search_evidence):
        """داخلي — يستخدم evidence النصي الجاهز."""
        url_norm = url.rstrip('/')
        name_found = name_appears_in_results(name, search_evidence)
        specific = is_specific_page(url)

        if specific and name_found:
            entry = add_to_registry(
                url=url, name_ar=name, name_en=name,
                section_type=section_type,
                owner='WebSearch Auto-Discovered',
                evidence=f'Auto-discovered: {search_evidence[:100]}',
            )
            self.verified[url_norm] = entry
            return Resolution('DISCOVERED', url, url, search_evidence[:80], name, section_type)

        add_rejection(url, f'Auto-rejected: specific={specific}, name_found={name_found}')
        self.rejected.add(url_norm)
        return Resolution('UNRESOLVABLE', url, None, 'Failed discovery', name, section_type)


# ── واجهة سطر الأوامر ────────────────────────────────────────────────────────

def cmd_check(args):
    """فحص رابط مقابل السجل (بدون WebSearch)."""
    resolver = SmartLinkResolver()
    res = resolver.resolve(args.url, args.name, args.section)
    data = res.to_dict()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    sys.exit(0 if res.ok else 1)


def cmd_add(args):
    """إضافة رابط يدويًا للسجل كـ HIGH_VERIFIED."""
    entry = add_to_registry(
        url=args.url,
        name_ar=args.name_ar,
        name_en=args.name_en or args.name_ar,
        section_type=args.type,
        owner=args.owner,
        evidence=args.evidence,
        verification='HIGH_VERIFIED',
    )
    print(f'✅ أُضيف: {entry["url"]}')
    print(json.dumps(entry, ensure_ascii=False, indent=2))


def cmd_reject(args):
    """رفض رابط وإضافته للقائمة السوداء."""
    add_rejection(args.url, args.reason)
    print(f'❌ رُفض: {args.url} — {args.reason}')


def cmd_lookup(args):
    """البحث عن رابط في السجل."""
    reg = load_registry()
    verified, rejected = build_lookup(reg)
    url_norm = args.url.rstrip('/')
    if url_norm in verified:
        print(json.dumps(verified[url_norm], ensure_ascii=False, indent=2))
    elif url_norm in rejected:
        print(f'REJECTED: {url_norm}')
        sys.exit(1)
    else:
        print(f'UNKNOWN: {url_norm} — غير موجود في السجل')
        sys.exit(2)


def cmd_resolve_with_search(args):
    """
    حل رابط بعد تلقي نتائج WebSearch (يُستخدم من Claude تلقائيًا).
    """
    resolver = SmartLinkResolver()
    res = resolver.resolve_with_search(
        url=args.url,
        name=args.name,
        section_type=args.section,
        search_title=args.title,
        search_snippet=args.snippet,
        owner=args.owner or '',
    )
    data = res.to_dict()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    sys.exit(0 if res.ok else 1)


def main():
    parser = argparse.ArgumentParser(
        description='SMART LINK RESOLUTION ENGINE v1.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أوامر:
  check     فحص رابط مقابل السجل
  add       إضافة رابط للسجل يدويًا كـ HIGH_VERIFIED
  reject    رفض رابط وإضافته للقائمة السوداء
  lookup    البحث عن رابط في السجل
  resolve   حل رابط بعد تلقي نتائج WebSearch

أمثلة:
  python scripts/smart_link_resolver.py check \\
    --url https://www.pmi.org/certifications/pmp \\
    --name "شهادة PMP" --section certification

  python scripts/smart_link_resolver.py add \\
    --url https://www.iia.org/en/certifications/cia/ \\
    --name-ar "شهادة المراجع الداخلي المعتمد — CIA" \\
    --name-en "Certified Internal Auditor (CIA)" \\
    --type certification --owner "IIA" \\
    --evidence "WebSearch CONFIRMED: Official IIA CIA page"

  python scripts/smart_link_resolver.py resolve \\
    --url https://www.coursera.org/learn/negotiation \\
    --name "مهارات التفاوض" --section course \\
    --title "Successful Negotiation: Essential Strategies and Skills | Coursera" \\
    --snippet "Learn negotiation strategies and skills. Offered by University of Michigan."
        """
    )
    sub = parser.add_subparsers(dest='command')

    # check
    p = sub.add_parser('check', help='فحص رابط مقابل السجل')
    p.add_argument('--url', required=True)
    p.add_argument('--name', default='')
    p.add_argument('--section', default='program',
                   choices=['program', 'certification', 'course'])

    # add
    p = sub.add_parser('add', help='إضافة رابط للسجل يدويًا')
    p.add_argument('--url', required=True)
    p.add_argument('--name-ar', required=True, dest='name_ar')
    p.add_argument('--name-en', default='', dest='name_en')
    p.add_argument('--type', required=True,
                   choices=['program', 'certification', 'course'])
    p.add_argument('--owner', required=True)
    p.add_argument('--evidence', required=True)

    # reject
    p = sub.add_parser('reject', help='رفض رابط')
    p.add_argument('--url', required=True)
    p.add_argument('--reason', required=True)

    # lookup
    p = sub.add_parser('lookup', help='البحث عن رابط في السجل')
    p.add_argument('--url', required=True)

    # resolve
    p = sub.add_parser('resolve', help='حل رابط بعد WebSearch')
    p.add_argument('--url', required=True)
    p.add_argument('--name', required=True)
    p.add_argument('--section', required=True,
                   choices=['program', 'certification', 'course'])
    p.add_argument('--title', required=True, help='عنوان الصفحة من WebSearch')
    p.add_argument('--snippet', required=True, help='مقتطف من WebSearch')
    p.add_argument('--owner', default='')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        'check': cmd_check,
        'add': cmd_add,
        'reject': cmd_reject,
        'lookup': cmd_lookup,
        'resolve': cmd_resolve_with_search,
    }
    dispatch[args.command](args)


if __name__ == '__main__':
    main()
