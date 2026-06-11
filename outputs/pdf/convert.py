import markdown
import re
import os
import sys
import base64
from weasyprint import HTML

# ── Social handles ────────────────────────────────────────────────────────────
X_USERNAME      = "tawjeeh_hub"
TIKTOK_USERNAME = "tawjeeh.hub"
INSTA_USERNAME  = "tawjeeh.hub"
SNAP_USERNAME   = "tawjeeh.hub"
YT_USERNAME     = "tawjeeh_hub"
WEBSITE         = "www.tawjeeh.hub"
X_URL           = f"https://x.com/{X_USERNAME}"
TIKTOK_URL      = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"
INSTA_URL       = f"https://instagram.com/{INSTA_USERNAME}"
SNAP_URL        = f"https://www.snapchat.com/add/{SNAP_USERNAME}"
YT_URL          = f"https://www.youtube.com/@{YT_USERNAME}"
WEBSITE_URL     = f"https://{WEBSITE}"

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
REPO_DIR  = os.path.dirname(os.path.dirname(BASE_DIR))
LOGO_FILE = os.path.join(REPO_DIR, "design_reference", "project_logo_watermark_transparent.png")
FONTS_DIR = os.path.join(REPO_DIR, "design_reference", "fonts")

if len(sys.argv) > 1:
    _src = os.path.abspath(sys.argv[1])
    _stem = os.path.splitext(os.path.basename(_src))[0]
    MD_FILE  = _src
    HTML_OUT = os.path.join(BASE_DIR, f"{_stem}.html")
    PDF_OUT  = os.path.join(BASE_DIR, f"{_stem}.pdf")
else:
    MD_FILE  = os.path.join(REPO_DIR, "outputs", "test_card_001_qadi.md")
    HTML_OUT = os.path.join(BASE_DIR, "test_card_001_qadi.html")
    PDF_OUT  = os.path.join(BASE_DIR, "test_card_001_qadi.pdf")

# ── Embed logo as base64 ──────────────────────────────────────────────────────
with open(LOGO_FILE, "rb") as f:
    LOGO_B64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()

# ── Footer platform icons (minimal inline SVGs, white strokes) ───────────────
def _svg_data_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

_SVG_STROKE = 'fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"'

# نوتة TikTok مبسطة بأشكال هندسية نظيفة — أسود أصلي يعكس هوية التطبيق
ICON_TIKTOK = _svg_data_uri(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#000000" stroke="none">'
    '<circle cx="9" cy="16.3" r="3.4"/>'
    '<path d="M12.4 3.6h2.7c.3 2.5 2 4.3 4.5 4.6v2.7c-1.7 0-3.2-.5-4.5-1.4v6.8'
    'c0 .2 0 .4-.1.6h-2.6c0-.2.1-.4.1-.6V3.6z"/></svg>'
)
# كاميرا إنستغرام بخطوط نظيفة فقط: مربع بزوايا دائرية + عدسة دائرية — بلا تفاصيل دقيقة تتشوش
ICON_INSTAGRAM = _svg_data_uri(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {_SVG_STROKE}>'
    f'<rect x="3.5" y="3.5" width="17" height="17" rx="5"/>'
    f'<circle cx="12" cy="12" r="4.2"/></svg>'
)
# شبح سناب شات بخطوط أبسط وأنعم — صورة أوضح عند الحجم الصغير
ICON_SNAPCHAT = _svg_data_uri(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {_SVG_STROKE}>'
    f'<path d="M12 4c2.4 0 4 1.9 4 4.4 0 1.6.1 3 .9 3.9.6.6 1.3.8 2 1'
    f'-.4.9-1.5 1.3-2.5 1.5 0 .6-.2 1.2-.7 1.2s-1-.3-1.7-.3c-.9 0-1.5.9-2 .9'
    f's-1.1-.9-2-.9c-.7 0-1.2.3-1.7.3s-.7-.6-.7-1.2c-1-.2-2.1-.6-2.5-1.5'
    f'.7-.2 1.4-.4 2-1 .8-.9.9-2.3.9-3.9C8 5.9 9.6 4 12 4z"/></svg>'
)
# حرف X بلونه الأصلي الأسود — تصميم نظيف ومتزن
ICON_X = _svg_data_uri(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#000000" stroke="none">'
    '<path d="M5.2 4.6h3.1l3.7 4.9 4-4.9h2.8L13.6 11l5.4 8.4h-3.1l-4-5.3-4.4 5.3H4.6l5.9-7.2z"/></svg>'
)
# مستطيل مدوّر + مثلث تشغيل واضح بنسب متوازنة — رمز يوتيوب الكلاسيكي
ICON_YOUTUBE = _svg_data_uri(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {_SVG_STROKE}>'
    f'<rect x="3" y="5.5" width="18" height="13" rx="3.5"/>'
    f'<path d="M10 9.3l5.2 2.7-5.2 2.7z" fill="#ffffff" stroke="none"/></svg>'
)
# كرة أرضية بسيطة: دائرة + خط استواء + خط طول واحد — وضوح أعلى دون تفاصيل زائدة
ICON_WEB = _svg_data_uri(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {_SVG_STROKE}>'
    f'<circle cx="12" cy="12" r="8.2"/>'
    f'<path d="M3.8 12h16.4M12 3.8c2.6 2.2 2.6 14.2 0 16.4"/></svg>'
)

# ── Section heading sets ──────────────────────────────────────────────────────
H2_HEADINGS = {
    'المسميات المكافئة', 'التصنيف الوطني SSC', 'طبيعة العمل',
    'المهام الرئيسية', 'المرتبة والراتب', 'المزايا الوظيفية',
    'الشروط والمؤهلات', 'متطلبات التقييم والتهيئة المهنية', 'الخبرات المطلوبة',
    'برامج التأهيل المعتمدة', 'الشهادات المهنية الاحترافية', 'المهارات المطلوبة',
    'الدورات الداعمة', 'جهات التوظيف وطرق التقديم',
    'المسار الوظيفي والتطور المهني', 'الملاحظات المهنية المتقدمة',
    'النصائح العملية الإضافية', 'جدول مدى قبول التخصصات',
}

# عناوين القطاعات — تظهر بلون المحتوى العادي (#023663)، لا باللون الرسمي للعناوين الفرعية
SECTOR_H3_HEADINGS = {
    'القطاع الحكومي', 'القطاع شبه الحكومي', 'القطاع الخاص',
    'القطاع غير الربحي', 'القطاع المستقل', 'العمل الحر',
    'الجهات الحكومية', 'الجهات شبه الحكومية',
    'الجهات الخاصة', 'الجهات غير الربحية', 'الجهات المستقلة',
}

# Structural sub-headings — rendered as h3 with official sub-heading color (#496379)
STRUCTURAL_H3_HEADINGS = {
    'جهات سبق وأعلنت',
    'جهات توظف لوجود ممارسة/وحدة/اختصاص',
    'جهات مستحدثة',
    'جهات ناشئة أو قليلة التنافس',
    'قبل التعيين', 'بعد التعيين',
    'الشروط العامة', 'شروط العمر', 'الشروط الإضافية',
    'الجهات الموصى بها', 'ملاحظة مهمة',
    'السلك القضائي — وزارة العدل وديوان المظالم',
}

H3_HEADINGS = SECTOR_H3_HEADINGS | STRUCTURAL_H3_HEADINGS

# ── Load & pre-process markdown ───────────────────────────────────────────────
with open(MD_FILE, encoding="utf-8") as f:
    lines = f.readlines()

processed = []
for line in lines:
    stripped = line.rstrip()
    if re.match(r'^\d+\.\s+\S', stripped) and len(stripped) < 35:
        title = re.sub(r'^\d+\.\s+', '', stripped)
        processed.append(f'# {title}\n')
    elif stripped in H2_HEADINGS:
        processed.append(f'## {stripped}\n')
    elif stripped in H3_HEADINGS:
        processed.append(f'### {stripped}\n')
    else:
        processed.append(line)

md_content = ''.join(processed)
md_content = re.sub(r'---\s*\n## سجل المصادر.*', '', md_content, flags=re.DOTALL)

html_body = markdown.markdown(md_content, extensions=['tables', 'nl2br'])

# Post-process: wrap "program link - institution:" so dotted underline + arrow
# covers the full label (program + institution) up to but not including the colon.
# Pattern: <a href="url">program</a> - institution:
def enhance_program_links(html):
    return re.sub(
        r'(<a href="[^"]+">)([^<]+)(</a>)([^:<\n]*?)(:)',
        lambda m: (
            m.group(1).replace('<a ', '<a class="linked-inline-label" ')
            + m.group(2)
            + m.group(4).rstrip()
            + ' <span class="linked-inline-arrow">↗</span>'
            + '</a>'
            + ':'
        ),
        html
    )

html_body = enhance_program_links(html_body)


def tag_sector_headings(html):
    for heading in SECTOR_H3_HEADINGS:
        html = html.replace(
            f'<h3>{heading}</h3>',
            f'<h3 class="sector-heading">{heading}</h3>',
        )
    return html

html_body = tag_sector_headings(html_body)

cover_match = re.search(r'<h1>(.*?)</h1>', html_body, re.DOTALL)
cover_title = cover_match.group(1) if cover_match else ''
# قاعدة عنوان المهنة: ما بين القوسين لا يظهر في الغلاف أو الهيدر
cover_title = re.sub(r'\s*\([^)]*\)', '', cover_title).strip()

# أقسام تستوجب بداية نظيفة — Visual Clean Page Lock
# إذا لم تكن المساحة كافية فوق الفوتر، تبدأ في صفحة جديدة
CLEAN_PAGE_SECTIONS = {
    # استثناءات يدوية فقط — المنطق التلقائي في CSS يتولى الحالات العامة
    # مثال: 'اسم قسم يحتاج إجبارًا دائمًا على صفحة جديدة'
}

# Replace h2 with section-heading divs, h3 with sub-heading divs
# Wrap each h2 section in a .section div
def transform_sections(html):
    # Split on h2 boundaries
    parts = re.split(r'(?=<h2>)', html)
    out = []
    for part in parts:
        if part.startswith('<h2>'):
            hm = re.match(r'<h2>(.*?)</h2>', part, re.DOTALL)
            if hm:
                heading = hm.group(1)
                body = part[hm.end():]
                extra = ' clean-page-required' if heading in CLEAN_PAGE_SECTIONS else ''
                out.append(
                    f'<div class="section{extra}">'
                    f'<div class="section-heading">{heading}</div>'
                    f'<div class="section-body">{body}</div>'
                    f'</div>'
                )
        # skip pre-h2 content (h1 is handled separately)
    return '\n'.join(out)

sections_html = transform_sections(html_body)


def tag_large_tables(html):
    """
    للجداول الكبيرة (أكثر من 4 صفوف أو مع thead):
    - إذا كانت .section مخصصة للجدول، تأخذ class إضافية table-page-group.
    - الجدول نفسه يأخذ table-page-block.
    - أي جدول كبير خارج هذا النمط يأخذ table-page-block منفردًا.
    """
    def is_large(t):
        return t.count('<tr') > 4 or '<thead>' in t

    SECTION_PAT = re.compile(
        r'<div class="section">'
        r'(<div class="section-heading">(?:(?!</div>).)*</div>)'
        r'(<div class="section-body">\s*)'
        r'(<table\b[^>]*>.*?</table>)',
        re.DOTALL,
    )

    def replace_section(m):
        table_html = m.group(3)
        if not is_large(table_html):
            return m.group(0)
        new_table = (table_html if 'table-page-block' in table_html
                     else table_html.replace('<table', '<table class="table-page-block"', 1))
        return (
            '<div class="section table-page-group">'
            + m.group(1) + m.group(2) + new_table
        )

    result = SECTION_PAT.sub(replace_section, html)

    def wrap_remaining(m):
        full = m.group(0)
        if 'table-page-block' in full:
            return full
        if is_large(full):
            return full.replace('<table', '<table class="table-page-block"', 1)
        return full
    result = re.sub(r'<table\b[^>]*>.*?</table>', wrap_remaining, result, flags=re.DOTALL)
    return result

sections_html = tag_large_tables(sections_html)


def guard_list_starts(html):
    """
    Human Layout Rule — تصنيف ذكي للقوائم:

    قائمة قصيرة (≤ SHORT_ITEMS عناصر أو نصها < SHORT_CHARS):
      → short-list-guard: الـUL كاملة كتلة صلبة، تنتقل للصفحة التالية إن لم تتسع.

    قائمة طويلة (> SHORT_ITEMS عناصر و نصها ≥ SHORT_CHARS):
      → long-list-flow: بدون قيد على الـUL، تتدفق بين الصفحات بحرية.
      كل li فيها محمي منفردًا بـ break-inside: avoid-page (CSS عام).

    لا تطبق على الجداول.
    """
    SHORT_ITEMS = 5     # قائمة بـ≤5 عناصر → قصيرة
    SHORT_CHARS = 550   # قائمة بنص <550 حرف → قصيرة

    def process_list(m):
        tag   = m.group(1)
        attrs = m.group(2)
        inner = m.group(3)

        li_parts = re.split(r'(?=<li[\s>])', inner)
        li_parts = [p for p in li_parts if p.strip()]

        if not li_parts:
            return m.group(0)

        text_chars = len(re.sub(r'<[^>]+>', '', inner))
        is_short = len(li_parts) <= SHORT_ITEMS or text_chars < SHORT_CHARS

        if is_short:
            # القائمة كاملة كتلة صلبة — تنتقل للصفحة التالية إن لم تتسع
            return (
                f'<div class="short-list-guard">'
                f'<{tag}{attrs}>{"".join(li_parts)}</{tag}>'
                f'</div>'
            )
        else:
            # القائمة الطويلة تتدفق بحرية — كل li محمي بـCSS العام
            return (
                f'<div class="long-list-flow">'
                f'<{tag}{attrs}>{"".join(li_parts)}</{tag}>'
                f'</div>'
            )

    return re.sub(
        r'<(ul|ol)([^>]*)>(.*?)</(ul|ol)>',
        process_list,
        html,
        flags=re.DOTALL,
    )


sections_html = guard_list_starts(sections_html)


def tag_acceptance_table(html):
    """
    Find the acceptance table section and:
    - wrap the table in a styled container div
    - inject badge <span> into the مدى القبول column (2nd td in each data row)
    """
    section_pat = re.compile(
        r'(<div class="[^"]*section[^"]*">'
        r'<div class="section-heading">جدول مدى قبول التخصصات</div>'
        r'<div class="section-body">)'
        r'(.*?)'
        r'(</div>\s*</div>)',
        re.DOTALL,
    )

    BADGE_MAP = {
        'عالي':  'badge-high',
        'متوسط': 'badge-medium',
        'ضعيف':  'badge-low',
    }

    def inject_badges(row_match):
        row_html = row_match.group(0)
        tds = list(re.finditer(r'<td([^>]*)>(.*?)</td>', row_html, re.DOTALL))
        if len(tds) < 2:
            return row_html
        second = tds[1]
        raw = re.sub(r'<[^>]+>', '', second.group(2)).strip()
        if raw not in BADGE_MAP:
            return row_html
        badge = f'<span class="{BADGE_MAP[raw]}">{raw}</span>'
        new_td = f'<td{second.group(1)} class="acceptance-level-cell">{badge}</td>'
        return row_html[:second.start()] + new_td + row_html[second.end():]

    def process_section(m):
        prefix, body, suffix = m.group(1), m.group(2), m.group(3)
        # inject badges row by row
        body = re.sub(r'<tr>.*?</tr>', inject_badges, body, flags=re.DOTALL)
        # wrap table in styled container — merge any existing class into acceptance-table
        watermark_img = (
            f'<img class="acceptance-table-watermark" src="{LOGO_B64}" alt="">'
        )
        body = re.sub(
            r'<table\b([^>]*?)>',
            lambda m: (
                '<div class="acceptance-table-wrapper">'
                + watermark_img
                + '<table class="acceptance-table'
                + (' ' + re.search(r'class="([^"]*)"', m.group(1)).group(1)
                   if re.search(r'class="([^"]*)"', m.group(1)) else '')
                + '">'
            ),
            body,
            count=1,
        )
        body = re.sub(r'(</table>)', r'\1</div>', body, count=1)
        return prefix + body + suffix

    return section_pat.sub(process_section, html)


sections_html = tag_acceptance_table(sections_html)

# ── CSS ────────────────────────────────────────────────────────────────────────
CSS_STR = f"""
/* ── Fonts (مضمّنة من design_reference/fonts) ────────── */
@font-face {{
  font-family: 'Noto Kufi Arabic';
  src: url('file://{FONTS_DIR}/NotoKufiArabic-Regular.ttf');
  font-weight: normal;
}}
@font-face {{
  font-family: 'Noto Kufi Arabic';
  src: url('file://{FONTS_DIR}/NotoKufiArabic-Bold.ttf');
  font-weight: bold;
}}
@font-face {{
  font-family: 'Noto Naskh Arabic';
  src: url('file://{FONTS_DIR}/NotoNaskhArabic-Regular.ttf');
  font-weight: normal;
}}
@font-face {{
  font-family: 'Noto Naskh Arabic';
  src: url('file://{FONTS_DIR}/NotoNaskhArabic-Bold.ttf');
  font-weight: bold;
}}
@font-face {{
  font-family: 'Aniq';
  src: url('file://{FONTS_DIR}/aa-aniq-bold.otf');
  font-weight: bold;
}}

/* ── Page layout ─────────────────────────────────────── */
@page {{
  size: A4;
  margin-top: 17mm;
  margin-right: 0;
  margin-bottom: 0;
  margin-left: 0;
}}

:root {{
  --page-top-safe-gap: 17mm;
  --footer-height: 12.5mm;
  --footer-safe-gap: 8mm;
  --footer-reserved: 32mm;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body {{
  direction: rtl;
  font-family: 'Noto Kufi Arabic', sans-serif;
  background: #ffffff;
  color: #023663;
}}

/* عدم ترك عنوان أو سطر معزول عند تقسيم الصفحات */
p, li, td, th {{
  orphans: 2;
  widows: 2;
}}

/* ── Fixed watermark — appears on every page ─────────── */
/* إحداثيات مطلقة لضمان الثبات الكامل على كل صفحات A4 (297mm × 210mm) */
.page-watermark {{
  position: fixed;
  top: 122mm;
  left: 105mm;
  transform: translate(-50%, -50%);
  width: 135mm;
  opacity: 0.30;
  z-index: 2;
  pointer-events: none;
}}

/* ── Fixed footer — full-width gradient bar, edge-to-edge on every page ── */
.footer {{
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 12.5mm;
  background: linear-gradient(90deg, #023e96 0%, #017593 50%, #01b68e 100%);
  border-radius: 0;
  box-sizing: border-box;
  z-index: 999;
  overflow: hidden;
}}

/* إضاءة ناعمة جدًا أعلى الشريط لإعطائه عمقًا خفيفًا دون مسّ التدرج الأساسي */
.footer::before {{
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 45%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.10) 0%, rgba(255, 255, 255, 0) 100%);
  pointer-events: none;
}}

/* صف مرن واحد موزّع على كامل العرض — عناصر بسيطة (أيقونة + نص) دون كبسولات ثقيلة */
.footer-inner {{
  position: relative;
  height: 12mm;
  width: 100%;
  box-sizing: border-box;
  padding: 0 14mm;
  display: flex;
  align-items: center;
  justify-content: space-between;
  direction: ltr;
}}

/* عنصر بسيط: أيقونة عارية بلا أي حاوية + يوزر بجانبها في سطر واحد */
.footer-link {{
  display: flex;
  align-items: center;
  gap: 1.5mm;
  flex: 0 0 auto;
}}

/* أيقونة صِرفة بلا خلفية ولا حدود ولا إطار — مجرد رمز SVG معروض مباشرة */
.footer-icon {{
  display: inline-block;
  width: 3.5mm;
  height: 3.5mm;
  flex-shrink: 0;
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
}}

/* دائرة صغيرة وناعمة جدًا خلف الأيقونات السوداء (TikTok / X) فقط، لإبراز اللون الأصلي فوق التدرج */
.footer-icon-on-light {{
  width: 2.6mm;
  height: 2.6mm;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.78);
  background-size: 1.9mm 1.9mm;
  padding: 0.45mm;
  box-sizing: content-box;
}}

.footer-link a {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  color: #ffffff;
  font-size: 7.8pt;
  font-weight: 700;
  letter-spacing: 0.2pt;
  text-decoration: none;
  text-shadow: 0 0.2mm 0.3mm rgba(0, 0, 0, 0.22);
}}

/* فاصل عمودي رفيع بلون تركوازي متناسق مع الطرف الأخضر من التدرج */
.footer-divider {{
  flex: 0 0 auto;
  width: 0.3mm;
  height: 6mm;
  background: rgba(120, 235, 210, 0.45);
  border-radius: 0.2mm;
}}

/* ── Main content ────────────────────────────────────── */
.content {{
  position: relative;
  z-index: 1;
  box-sizing: border-box;
  /* padding-top: 0 — الهامش العلوي كله من @page margin-top: 17mm */
  padding: 0 17mm 32mm 17mm;
}}

/* ── Profession title ────────────────────────────────── */
.profession-title {{
  font-family: 'Aniq', 'Noto Naskh Arabic', serif;
  font-size: 17pt;
  font-weight: bold;
  color: #049e9e;
  text-align: right;
  margin-bottom: 5mm;
  line-height: 1.25;
}}

/* ── Section: تدفق ذكي — لا حبس للكتلة كاملة، العنوان يبقى مع بداية محتواه ── */
.section {{
  margin-bottom: 4mm;
  break-inside: auto;
  page-break-inside: auto;
  orphans: 3;
  widows: 3;
}}

/* لا يُترك العنوان وحيدًا في آخر الصفحة — يبقى ملتصقًا بأول أسطر محتواه */
.section-heading {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  font-size: 12pt;
  font-weight: bold;
  color: #5e4360;
  text-align: right;
  margin-bottom: 2mm;
  line-height: 1.4;
  background: none;
  break-after: avoid;
  page-break-after: avoid;
}}

/* محتوى العنصر — يتدفق بحرية بين الصفحات */
.section-body {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  font-size: 10pt;
  color: #023663;
  text-align: right;
  line-height: 1.72;
  break-inside: auto;
  page-break-inside: auto;
  orphans: 3;
  widows: 3;
}}

/* Visual Clean Page Lock — تلقائي */
.section-body > *:first-child {{
  break-before: avoid;
  page-break-before: avoid;
}}
.section-body > *:nth-child(2) {{
  break-before: avoid;
  page-break-before: avoid;
}}

/* عناوين فرعية بنيوية (جهات سبق وأعلنت، قبل التعيين، إلخ) — باللون الرسمي للعناوين الفرعية */
.section-body h3 {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  font-size: 11.5pt;
  font-weight: bold;
  color: #496379;
  margin-top: 2.6mm;
  margin-bottom: 1mm;
  break-after: avoid;
  page-break-after: avoid;
}}

/* عناوين القطاعات (القطاع الحكومي، القطاع الخاص، إلخ) — بارزة لكن بلون المحتوى */
.section-body h3.sector-heading {{
  color: #023663;
}}

.section-body p  {{
  margin-bottom: 1.4mm;
  break-inside: avoid-page;
}}

.section-body .sector-label {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  font-size: 10.5pt;
  font-weight: 700;
  color: #023663;
  margin-top: 2.6mm;
  margin-bottom: 1mm;
}}

.section-body .employment-sector {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  font-size: 11.5pt;
  font-weight: 700;
  color: #023663;
  margin-top: 3mm;
  margin-bottom: 1.2mm;
  break-after: avoid;
  page-break-after: avoid;
}}

.section-body .employment-subcategory {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  font-size: 10pt;
  font-weight: 700;
  color: #496379;
  margin-top: 2mm;
  margin-bottom: 0.8mm;
  break-after: avoid;
  page-break-after: avoid;
}}

.section-body .condition-label {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  font-size: 1.08em;
  font-weight: 700;
  color: #496379;
}}

.section-body .experience-entity {{
  color: #023663;
  font-family: 'Noto Kufi Arabic', sans-serif;
  font-weight: 700;
  font-size: 10.8pt;
}}

.section-body .assessment-entity {{
  color: #023663;
  font-family: 'Noto Kufi Arabic', sans-serif;
  font-weight: 700;
  font-size: 10.8pt;
  display: block;
  margin: 1.8mm 0 1mm 0;
}}

.section-body ul,
.section-body ol {{
  padding-right: 5mm;
  padding-left: 0;
  margin-top: 1.4mm;
  margin-bottom: 2.2mm;
  list-style-type: disc;
  list-style-position: outside;
}}
.section-body li {{
  margin-bottom: 1.2mm;
  line-height: 1.68;
  break-inside: avoid-page;
  page-break-inside: avoid;
}}
.section-body li::marker {{
  color: #023663;
  font-size: 1.35em;
}}

.section-body a {{
  color: #023663;
  text-decoration: none;
  font-size: inherit;
}}
.section-body a.linked-inline-label {{
  color: #023663;
  text-decoration-line: underline;
  text-decoration-style: dotted;
  text-decoration-color: #023663;
  text-decoration-thickness: 0.3mm;
  text-underline-offset: 0.65mm;
  font-weight: inherit;
  font-size: inherit;
}}
.section-body .linked-inline-arrow {{
  font-size: 0.88em;
  color: #023663;
  font-weight: 400;
}}
.section-body strong {{ font-weight: bold; color: #023663; }}

/* ── Tables ──────────────────────────────────────────────── */
.section-body table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 8.5pt;
  line-height: 1.4;
  margin-top: 1.6mm;
  color: #023663;
  break-inside: avoid;
  page-break-inside: avoid;
}}
.section-body thead, .section-body tbody, .section-body tfoot {{
  break-inside: avoid;
  page-break-inside: avoid;
}}
.section-body thead {{
  display: table-header-group;
}}
.section-body tr {{
  break-inside: avoid;
  page-break-inside: avoid;
}}
/* Human Layout Rule — القائمة القصيرة تنتقل كاملة إذا لم تتسع */
.short-list-guard {{
  break-inside: avoid-page;
  page-break-inside: avoid;
  display: block;
}}

/* القائمة الطويلة تتدفق بحرية — كل li محمي بالقاعدة العامة أدناه */
.long-list-flow {{
  display: block;
}}

/* Visual Clean Page Lock — قسم يستوجب بداية نظيفة فوق الفوتر */
.section.clean-page-required {{
  break-before: page;
  page-break-before: always;
}}

/* قسم كامل (عنوان + جدول) ينتقلان معًا إلى صفحة جديدة */
.section.table-page-group {{
  break-before: page;
  page-break-before: always;
  break-inside: avoid;
  page-break-inside: avoid;
  padding-top: 0;
}}
/* جدول كبير منفرد — يبدأ في صفحة جديدة */
.section-body table.table-page-block {{
  break-before: page;
  page-break-before: always;
  break-inside: avoid;
  page-break-inside: avoid;
  margin-top: 0;
}}
/* جدول داخل قسم table-page-group — لا كسر إضافي */
.section.table-page-group .section-body table.table-page-block {{
  break-before: auto;
  page-break-before: auto;
}}
.section-body th {{
  background: #023663;
  color: #ffffff;
  padding: 1.3mm 2.2mm;
  text-align: center;
  font-weight: bold;
  font-size: 8.5pt;
  vertical-align: middle;
}}
.section-body td {{
  padding: 1.3mm 2.2mm;
  border: 1px solid #c8d8e8;
  text-align: center;
  vertical-align: top;
}}
.section-body tr:nth-child(even) td {{ background: #f0f5fa; }}

/* ── Acceptance Table ─────────────────────────────────────── */
.acceptance-table-wrapper {{
  position: relative;
  border-radius: 3mm;
  overflow: hidden;
  box-shadow: 0 0.8mm 3mm rgba(2, 54, 99, 0.13);
  margin-top: 2mm;
}}

.acceptance-table-watermark {{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120mm;
  opacity: 0.045;
  z-index: 0;
  pointer-events: none;
}}

.section-body .acceptance-table {{
  position: relative;
  z-index: 1;
  width: 100%;
  border-collapse: collapse;
  font-size: 8.5pt;
  line-height: 1.45;
  margin-top: 0;
  table-layout: fixed;
}}

.section-body .acceptance-table th {{
  background: #023663;
  color: #ffffff;
  padding: 2mm 2.5mm;
  text-align: center;
  font-weight: bold;
  font-size: 8.5pt;
  vertical-align: middle;
  border: none;
}}

/* Column widths: التخصص | مدى القبول | سبب التقييم | متطلبات القبول | ملاحظات */
.section-body .acceptance-table th:nth-child(1),
.section-body .acceptance-table td:nth-child(1) {{ width: 13%; text-align: right; }}
.section-body .acceptance-table th:nth-child(2),
.section-body .acceptance-table td:nth-child(2) {{ width: 10%; text-align: center; }}
.section-body .acceptance-table th:nth-child(3),
.section-body .acceptance-table td:nth-child(3) {{ width: 24%; text-align: right; }}
.section-body .acceptance-table th:nth-child(4),
.section-body .acceptance-table td:nth-child(4) {{ width: 29%; text-align: right; }}
.section-body .acceptance-table th:nth-child(5),
.section-body .acceptance-table td:nth-child(5) {{ width: 24%; text-align: right; }}

.section-body .acceptance-table td {{
  padding: 2mm 2.5mm;
  border: 0.25mm solid #c8d8e8;
  vertical-align: middle;
  color: #023663;
  font-size: 8.5pt;
}}

.section-body .acceptance-table tr:nth-child(odd) td  {{ background: #ffffff; }}
.section-body .acceptance-table tr:nth-child(even) td {{ background: #f2f6fb; }}

.section-body .acceptance-table .acceptance-level-cell {{
  text-align: center;
  vertical-align: middle;
  padding: 1.5mm 1.5mm;
}}

/* اسم التخصص — أثقل وأكبر من بقية الخلايا */
.section-body .acceptance-table td:nth-child(1) {{
  font-size: 10.5pt;
  font-weight: 700;
  color: #023663;
  line-height: 1.45;
}}

/* شارات مدى القبول — داخل الخلية تمامًا */
.badge-high,
.badge-medium,
.badge-low {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  box-sizing: border-box;
  margin: 0 auto;
  min-width: 15mm;
  max-width: 100%;
  padding: 1.2mm 3mm;
  border-radius: 10mm;
  font-size: 7.8pt;
  font-weight: bold;
  color: #ffffff;
  line-height: 1;
  text-align: center;
}}

.badge-high   {{ background: #049E9E; }}
.badge-medium {{ background: #007F9E; }}
.badge-low    {{ background: #5E4360; }}
"""

# ── Footer HTML ───────────────────────────────────────────────────────────────
footer_html = f"""<div class="footer">
  <div class="footer-inner">
    <span class="footer-link"><span class="footer-icon footer-icon-on-light" style="background-image:url('{ICON_TIKTOK}')"></span><a href="{TIKTOK_URL}">{TIKTOK_USERNAME}</a></span>
    <span class="footer-divider"></span>
    <span class="footer-link"><span class="footer-icon" style="background-image:url('{ICON_INSTAGRAM}')"></span><a href="{INSTA_URL}">{INSTA_USERNAME}</a></span>
    <span class="footer-divider"></span>
    <span class="footer-link"><span class="footer-icon" style="background-image:url('{ICON_SNAPCHAT}')"></span><a href="{SNAP_URL}">{SNAP_USERNAME}</a></span>
    <span class="footer-divider"></span>
    <span class="footer-link"><span class="footer-icon footer-icon-on-light" style="background-image:url('{ICON_X}')"></span><a href="{X_URL}">{X_USERNAME}</a></span>
    <span class="footer-divider"></span>
    <span class="footer-link"><span class="footer-icon" style="background-image:url('{ICON_YOUTUBE}')"></span><a href="{YT_URL}">{YT_USERNAME}</a></span>
    <span class="footer-divider"></span>
    <span class="footer-link"><span class="footer-icon" style="background-image:url('{ICON_WEB}')"></span><a href="{WEBSITE_URL}">{WEBSITE}</a></span>
  </div>
</div>"""

watermark_html = f'<img class="page-watermark" src="{LOGO_B64}" alt="">'

# ── Assemble HTML ─────────────────────────────────────────────────────────────
full_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <style>{CSS_STR}</style>
</head>
<body>
{watermark_html}
{footer_html}
<div class="content">
  <div class="profession-title">{cover_title}</div>
  {sections_html}
</div>
</body>
</html>"""

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(full_html)
print(f"HTML → {HTML_OUT}")

HTML(HTML_OUT).write_pdf(PDF_OUT)
print(f"PDF  → {PDF_OUT}")
