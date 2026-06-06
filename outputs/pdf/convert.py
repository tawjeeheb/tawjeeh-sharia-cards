import markdown
import re
import os
import base64
from weasyprint import HTML

# ── Social handles ───────────────────────────────────────────────────────────
X_USERNAME      = "tawjeeh_hub"
TIKTOK_USERNAME = "tawjeeh.hub"
WEBSITE         = "www.tawjeeh.com"
X_URL           = f"https://x.com/{X_USERNAME}"
TIKTOK_URL      = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"
WEBSITE_URL     = f"https://{WEBSITE}"

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
REPO_DIR  = os.path.dirname(os.path.dirname(BASE_DIR))
MD_FILE   = os.path.join(REPO_DIR, "outputs", "test_card_001_qadi.md")
LOGO_FILE = os.path.join(REPO_DIR, "design_reference", "tawjeeh_logo.jpeg")
HTML_OUT  = os.path.join(BASE_DIR, "test_card_001_qadi.html")
PDF_OUT   = os.path.join(BASE_DIR, "test_card_001_qadi.pdf")

# ── Embed logo as base64 ─────────────────────────────────────────────────────
with open(LOGO_FILE, "rb") as f:
    LOGO_B64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()

# ── Section heading sets ─────────────────────────────────────────────────────
H2_HEADINGS = {
    'المسميات المكافئة', 'التصنيف الوطني SSC', 'طبيعة العمل',
    'المهام الرئيسية', 'الراتب والدرجة الوظيفية', 'المزايا والحوافز',
    'الشروط والمؤهلات', 'التقييم والإلحاق الوظيفي', 'الخبرة المطلوبة',
    'البرامج التدريبية المعتمدة', 'الشهادات المهنية', 'المهارات المطلوبة',
    'الدورات الداعمة', 'جهات التوظيف وطريقة التقديم',
    'المسار الوظيفي والتطور المهني', 'الملاحظات المهنية المتقدمة',
    'النصائح العملية الإضافية', 'جدول مدى قبول التخصصات',
}
H3_HEADINGS = {
    'الجهات الحكومية', 'القطاع الحكومي', 'القطاع الخاص',
    'القطاع غير الربحي', 'العمل الحر', 'الجهات الموصى بها', 'ملاحظة مهمة',
}

# ── Load & pre-process markdown ──────────────────────────────────────────────
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

# ── Extract cover title & section cards ──────────────────────────────────────
cover_match = re.search(r'<h1>(.*?)</h1>', html_body, re.DOTALL)
cover_title = cover_match.group(1) if cover_match else ''

raw_sections = re.split(r'(?=<h2>)', html_body)
section_cards = []
for part in raw_sections:
    if not part.strip() or not part.startswith('<h2>'):
        continue
    hm = re.match(r'<h2>(.*?)</h2>', part, re.DOTALL)
    if not hm:
        continue
    section_cards.append((hm.group(1), part[hm.end():]))

# ── Watermark (logo image, centered, 30% opacity) ────────────────────────────
def watermark_html():
    return f'<img class="page-watermark" src="{LOGO_B64}" alt="watermark">'

# ── Footer (matches reference: dark bar + handles) ───────────────────────────
def footer_html():
    return f"""<div class="page-footer">
  <a class="footer-handle" href="{TIKTOK_URL}">&#9654; {TIKTOK_USERNAME}</a>
  <span class="footer-dot">&#9679;</span>
  <a class="footer-handle" href="{X_URL}">&#x1D54F; {X_USERNAME}</a>
  <span class="footer-dot">&#9679;</span>
  <a class="footer-handle" href="{WEBSITE_URL}">{WEBSITE}</a>
</div>"""

# ── Page header (content pages only) ─────────────────────────────────────────
def page_header_html():
    return f"""<div class="page-header">
  <span class="page-header-title">{cover_title}</span>
  <img class="page-header-logo" src="{LOGO_B64}" alt="Tawjeeh HUB">
</div>
<div class="page-accent-bar"></div>"""

# ── Build pages ───────────────────────────────────────────────────────────────
SECTIONS_PER_PAGE = 3
pages = []

# Cover page — minimal, logo watermark centered, footer bar
pages.append(f"""<div class="cover-page">
  {watermark_html()}
  <div class="cover-content">
    <div class="cover-label">بطاقة المهنة الشرعية</div>
    <div class="cover-profession">{cover_title}</div>
  </div>
  {footer_html()}
</div>""")

# Content pages
for i in range(0, len(section_cards), SECTIONS_PER_PAGE):
    chunk = section_cards[i:i + SECTIONS_PER_PAGE]
    cards_html = ''
    for heading, body in chunk:
        cards_html += f"""<div class="section-card">
  <div class="section-heading">{heading}</div>
  <div class="section-body">{body}</div>
</div>
"""
    pages.append(f"""<div class="content-page">
  {page_header_html()}
  {watermark_html()}
  <div class="page-body">{cards_html}</div>
  {footer_html()}
</div>""")

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS_STR = """
@font-face {
  font-family: 'NotoKufi';
  src: url('/usr/share/fonts/truetype/noto/NotoKufiArabic-Regular.ttf');
  font-weight: normal;
}
@font-face {
  font-family: 'NotoKufi';
  src: url('/usr/share/fonts/truetype/noto/NotoKufiArabic-Bold.ttf');
  font-weight: bold;
}
@font-face {
  font-family: 'NotoNaskh';
  src: url('/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf');
  font-weight: normal;
}
@font-face {
  font-family: 'NotoNaskh';
  src: url('/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf');
  font-weight: bold;
}

@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  direction: rtl;
  font-family: 'NotoKufi', sans-serif;
  background: #ffffff;
  color: #023663;
  font-size: 10.5pt;
  line-height: 1.85;
}

/* ── Watermark image ───────────────────────── */
.page-watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120mm;
  opacity: 0.30;
  pointer-events: none;
  z-index: 0;
}

/* ── Cover page ────────────────────────────── */
.cover-page {
  width: 210mm;
  height: 297mm;
  background: #ffffff;
  position: relative;
  page-break-after: always;
  overflow: hidden;
}

.cover-content {
  position: absolute;
  top: 18mm;
  left: 20mm;
  right: 20mm;
  text-align: center;
  z-index: 1;
  direction: rtl;
}

.cover-label {
  font-family: 'NotoNaskh', serif;
  font-size: 13pt;
  color: #5e4360;
  font-weight: bold;
  margin-bottom: 8mm;
  letter-spacing: 0.04em;
  width: 100%;
  text-align: center;
}

.cover-profession {
  font-family: 'NotoNaskh', serif;
  font-size: 52pt;
  font-weight: bold;
  color: #049e9e;
  line-height: 1.1;
  width: 100%;
  text-align: center;
}

/* ── Content page ──────────────────────────── */
.content-page {
  width: 210mm;
  min-height: 297mm;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  position: relative;
  page-break-after: always;
  overflow: hidden;
}

.page-header {
  width: 100%;
  background: #023663;
  padding: 3.5mm 10mm;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}

.page-header-title {
  font-family: 'NotoNaskh', serif;
  font-size: 12pt;
  font-weight: bold;
  color: #ffffff;
}

.page-header-logo {
  height: 10mm;
  opacity: 1;
  filter: brightness(0) invert(1);
}

.page-accent-bar {
  width: 100%;
  height: 2.5mm;
  background: #049e9e;
  position: relative;
  z-index: 1;
}

.page-body {
  flex: 1;
  padding: 7mm 12mm 5mm;
  position: relative;
  z-index: 1;
}

/* ── Section card ──────────────────────────── */
.section-card {
  background: #f8fafc;
  border-radius: 5px;
  border-right: 4px solid #049e9e;
  margin-bottom: 5mm;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(2,54,99,0.08);
}

.section-heading {
  background: #023663;
  color: #ffffff;
  font-family: 'NotoNaskh', serif;
  font-size: 11pt;
  font-weight: bold;
  padding: 2.5mm 5mm;
  color: #ffffff;
}

/* override: element name color as specified (#5e4360) via sub-heading */
.section-body h3 {
  font-family: 'NotoNaskh', serif;
  font-size: 10.5pt;
  font-weight: bold;
  color: #5e4360;
  margin: 3mm 0 1.5mm;
  padding-right: 3mm;
  border-right: 3px solid #5e4360;
}

.section-body {
  padding: 4mm 6mm;
  color: #023663;
  font-size: 10pt;
}

.section-body ul, .section-body ol {
  padding-right: 5mm;
  margin-top: 1mm;
}
.section-body li { margin-bottom: 0.8mm; }
.section-body p  { margin-bottom: 1.2mm; }
.section-body a  { color: #049e9e; text-decoration: none; }
.section-body strong { color: #023663; }

/* tables */
.section-body table {
  width: 100%;
  border-collapse: collapse;
  font-size: 9pt;
  margin-top: 2mm;
}
.section-body th {
  background: #023663;
  color: #ffffff;
  padding: 2mm 3mm;
  text-align: center;
  font-weight: bold;
}
.section-body td {
  padding: 1.8mm 3mm;
  border: 1px solid #cdd9e5;
  text-align: center;
  color: #023663;
}
.section-body tr:nth-child(even) td { background: #eef3f8; }

/* ── Footer (matches reference: solid dark bar, centered handles) ── */
.page-footer {
  width: 100%;
  background: #1a2e44;
  padding: 3.5mm 10mm;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5mm;
  flex-direction: row;
  z-index: 2;
  direction: ltr;
}
/* On cover page footer is absolute-positioned at bottom */
.cover-page .page-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

.footer-handle {
  font-family: 'NotoKufi', sans-serif;
  font-size: 8.5pt;
  color: #049e9e;
  text-decoration: none;
  white-space: nowrap;
}

.footer-dot {
  color: rgba(255,255,255,0.25);
  font-size: 5pt;
}
"""

full_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <style>{CSS_STR}</style>
</head>
<body>
{''.join(pages)}
</body>
</html>"""

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(full_html)
print(f"HTML → {HTML_OUT}")

HTML(HTML_OUT).write_pdf(PDF_OUT)
print(f"PDF  → {PDF_OUT}")
