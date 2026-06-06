import markdown
import re
import os
from weasyprint import HTML, CSS

# ── Social handles (edit here) ──────────────────────────────────────────────
X_USERNAME      = "tawjeeh_hub"
TIKTOK_USERNAME = "tawjeeh.hub"
X_URL           = f"https://x.com/{X_USERNAME}"
TIKTOK_URL      = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"
LOGO_TEXT_AR    = "مركز توجيه"
LOGO_TEXT_EN    = "Tawjeeh HUB"

# ── Section heading sets ─────────────────────────────────────────────────────
H2_HEADINGS = {
    'المسميات المكافئة',
    'التصنيف الوطني SSC',
    'طبيعة العمل',
    'المهام الرئيسية',
    'الراتب والدرجة الوظيفية',
    'المزايا والحوافز',
    'الشروط والمؤهلات',
    'التقييم والإلحاق الوظيفي',
    'الخبرة المطلوبة',
    'البرامج التدريبية المعتمدة',
    'الشهادات المهنية',
    'المهارات المطلوبة',
    'الدورات الداعمة',
    'جهات التوظيف وطريقة التقديم',
    'المسار الوظيفي والتطور المهني',
    'الملاحظات المهنية المتقدمة',
    'النصائح العملية الإضافية',
    'جدول مدى قبول التخصصات',
}

H3_HEADINGS = {
    'الجهات الحكومية',
    'القطاع الحكومي',
    'القطاع الخاص',
    'القطاع غير الربحي',
    'العمل الحر',
    'الجهات الموصى بها',
    'ملاحظة مهمة',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
MD_FILE  = os.path.join(REPO_DIR, "outputs", "test_card_001_qadi.md")
HTML_OUT = os.path.join(BASE_DIR, "test_card_001_qadi.html")
PDF_OUT  = os.path.join(BASE_DIR, "test_card_001_qadi.pdf")

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

# ── Extract cover title & sections ──────────────────────────────────────────
cover_match = re.search(r'<h1>(.*?)</h1>', html_body, re.DOTALL)
cover_title = cover_match.group(1) if cover_match else ''

# Split on h2 tags to get individual section content blocks
raw_sections = re.split(r'(?=<h2>)', html_body)
section_cards = []
for part in raw_sections:
    if not part.strip() or not part.startswith('<h2>'):
        continue
    hm = re.match(r'<h2>(.*?)</h2>', part, re.DOTALL)
    if not hm:
        continue
    heading = hm.group(1)
    body    = part[hm.end():]
    section_cards.append((heading, body))

# ── Footer & header HTML ──────────────────────────────────────────────────────
def footer_html():
    return f"""<div class="page-footer">
  <span class="footer-brand">{LOGO_TEXT_AR} | {LOGO_TEXT_EN}</span>
  <div class="footer-links">
    <a class="footer-link" href="{X_URL}">&#x1D54F; @{X_USERNAME}</a>
    <span class="footer-sep">|</span>
    <a class="footer-link" href="{TIKTOK_URL}">TikTok @{TIKTOK_USERNAME}</a>
  </div>
</div>"""

def page_header_html():
    return f"""<div class="page-header">
  <span class="page-header-title">{cover_title}</span>
  <span class="page-header-brand">{LOGO_TEXT_EN}</span>
</div>
<div class="page-accent-bar"></div>"""

def watermark_html():
    return f'<div class="page-watermark">{LOGO_TEXT_AR}<br>{LOGO_TEXT_EN}</div>'

# ── Build pages ───────────────────────────────────────────────────────────────
SECTIONS_PER_PAGE = 3
pages = []

# Cover page
pages.append(f"""<div class="cover-page">
  <div class="cover-top-bar"></div>
  <div class="cover-accent-bar"></div>
  {watermark_html()}
  <div class="cover-content">
    <div class="cover-label">بطاقة المهنة الشرعية</div>
    <div class="cover-profession">{cover_title}</div>
    <div class="cover-divider"></div>
    <div class="cover-brand">{LOGO_TEXT_AR}</div>
    <div class="cover-brand-en">{LOGO_TEXT_EN}</div>
  </div>
  {footer_html()}
</div>""")

# Content pages: group sections
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
  background: #f4f6f9;
  color: #023663;
  font-size: 10.5pt;
  line-height: 1.85;
}

/* ── Cover ─────────────────────────────── */
.cover-page {
  width: 210mm;
  min-height: 297mm;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  position: relative;
  page-break-after: always;
  overflow: hidden;
}
.cover-top-bar  { width: 100%; height: 14mm; background: #023663; }
.cover-accent-bar { width: 100%; height: 5mm; background: #049e9e; }

.cover-watermark {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'NotoNaskh', serif;
  font-size: 68pt;
  font-weight: bold;
  color: rgba(2,54,99,0.07);
  white-space: nowrap;
  text-align: center;
  line-height: 1.25;
  pointer-events: none;
}

.cover-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 18mm 22mm;
  text-align: center;
  position: relative;
  z-index: 1;
}
.cover-label {
  font-family: 'NotoNaskh', serif;
  font-size: 13pt;
  color: #5e4360;
  font-weight: bold;
  margin-bottom: 8mm;
}
.cover-profession {
  font-family: 'NotoNaskh', serif;
  font-size: 44pt;
  font-weight: bold;
  color: #049e9e;
  line-height: 1.15;
  margin-bottom: 10mm;
}
.cover-divider {
  width: 55mm; height: 2px;
  background: linear-gradient(to left, transparent, #049e9e, transparent);
  margin-bottom: 10mm;
}
.cover-brand {
  font-family: 'NotoNaskh', serif;
  font-size: 16pt;
  font-weight: bold;
  color: #023663;
}
.cover-brand-en {
  font-size: 11pt;
  color: #5e4360;
  margin-top: 2mm;
}

/* ── Content page ──────────────────────── */
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
  padding: 4mm 12mm;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.page-header-title {
  font-family: 'NotoNaskh', serif;
  font-size: 12pt;
  font-weight: bold;
  color: #ffffff;
}
.page-header-brand {
  font-size: 9pt;
  color: #049e9e;
  font-family: 'NotoKufi', sans-serif;
}
.page-accent-bar { width: 100%; height: 3mm; background: #049e9e; }

.page-watermark {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'NotoNaskh', serif;
  font-size: 50pt;
  font-weight: bold;
  color: rgba(2,54,99,0.045);
  white-space: nowrap;
  text-align: center;
  line-height: 1.25;
  pointer-events: none;
  z-index: 0;
}

.page-body {
  flex: 1;
  padding: 7mm 12mm 5mm;
  position: relative;
  z-index: 1;
}

/* ── Section card ──────────────────────── */
.section-card {
  background: #f8fafc;
  border-radius: 5px;
  border-right: 4px solid #049e9e;
  margin-bottom: 5mm;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(2,54,99,0.08);
}
.section-heading {
  background: #023663;
  color: #ffffff;
  font-family: 'NotoNaskh', serif;
  font-size: 11.5pt;
  font-weight: bold;
  padding: 2.5mm 5mm;
}
.section-body {
  padding: 4mm 6mm;
  color: #023663;
  font-size: 10pt;
}
.section-body h3 {
  font-family: 'NotoNaskh', serif;
  font-size: 10.5pt;
  font-weight: bold;
  color: #5e4360;
  margin: 3mm 0 1.5mm;
  padding-right: 3mm;
  border-right: 3px solid #5e4360;
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

/* ── Footer ───────────────────────────── */
.page-footer {
  width: 100%;
  background: #023663;
  padding: 3mm 12mm;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.footer-brand {
  font-family: 'NotoNaskh', serif;
  font-size: 9pt;
  color: #ffffff;
  font-weight: bold;
}
.footer-links {
  display: flex;
  align-items: center;
  gap: 6mm;
  direction: ltr;
}
.footer-link {
  font-size: 8.5pt;
  color: #049e9e;
  text-decoration: none;
  font-family: 'NotoKufi', sans-serif;
}
.footer-sep { color: rgba(255,255,255,0.3); font-size: 9pt; }
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
