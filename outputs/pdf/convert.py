import markdown
import re
import os
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
WEBSITE_URL     = f"https://{WEBSITE}"

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
REPO_DIR  = os.path.dirname(os.path.dirname(BASE_DIR))
MD_FILE   = os.path.join(REPO_DIR, "outputs", "test_card_001_qadi.md")
LOGO_FILE = os.path.join(REPO_DIR, "design_reference", "tawjeeh_logo.jpeg")
HTML_OUT  = os.path.join(BASE_DIR, "test_card_001_qadi.html")
PDF_OUT   = os.path.join(BASE_DIR, "test_card_001_qadi.pdf")

# ── Embed logo as base64 ──────────────────────────────────────────────────────
with open(LOGO_FILE, "rb") as f:
    LOGO_B64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()

# ── Section heading sets ──────────────────────────────────────────────────────
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

# ── Extract cover title & section HTML ───────────────────────────────────────
cover_match = re.search(r'<h1>(.*?)</h1>', html_body, re.DOTALL)
cover_title = cover_match.group(1) if cover_match else ''

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
                out.append(
                    f'<div class="section" style="break-inside: avoid;">'
                    f'<div class="section-heading">{heading}</div>'
                    f'<div class="section-body">{body}</div>'
                    f'</div>'
                )
        # skip pre-h2 content (h1 is handled separately)
    return '\n'.join(out)

sections_html = transform_sections(html_body)

# ── CSS ────────────────────────────────────────────────────────────────────────
CSS_STR = f"""
/* ── Fonts ──────────────────────────────────────────── */
@font-face {{
  font-family: 'NotoKufi';
  src: url('/usr/share/fonts/truetype/noto/NotoKufiArabic-Regular.ttf');
  font-weight: normal;
}}
@font-face {{
  font-family: 'NotoKufi';
  src: url('/usr/share/fonts/truetype/noto/NotoKufiArabic-Bold.ttf');
  font-weight: bold;
}}
@font-face {{
  font-family: 'NotoNaskh';
  src: url('/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf');
  font-weight: normal;
}}
@font-face {{
  font-family: 'NotoNaskh';
  src: url('/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf');
  font-weight: bold;
}}

/* ── Page layout ─────────────────────────────────────── */
@page {{
  size: A4;
  /* top | right | bottom (footer ~14mm) | left */
  margin: 14mm 18mm 20mm 16mm;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body {{
  direction: rtl;
  font-family: 'NotoKufi', sans-serif;
  background: #ffffff;
  color: #023663;
}}

/* ── Fixed watermark — appears on every page ─────────── */
.page-watermark {{
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 105mm;
  opacity: 0.30;
  z-index: 0;
  pointer-events: none;
}}

/* ── Fixed footer — appears on every page ────────────── */
.page-footer {{
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
}}

.footer-teal-bar {{
  height: 2.5mm;
  background: #049e9e;
}}

.footer-inner {{
  background: #12263a;
  padding: 2.5mm 5mm;
  display: flex;
  align-items: center;
  justify-content: space-between;
  direction: ltr;
}}

.footer-handles {{
  display: flex;
  align-items: center;
  gap: 4mm;
}}

.fh {{
  font-family: 'NotoKufi', sans-serif;
  font-size: 7pt;
  color: #9dbdd6;
  text-decoration: none;
  white-space: nowrap;
}}

.fi {{ color: #049e9e; margin-left: 0.5mm; }}

.footer-arrow {{
  font-size: 13pt;
  color: #049e9e;
  font-weight: bold;
  line-height: 1;
}}

/* ── Main content ────────────────────────────────────── */
.content {{
  position: relative;
  z-index: 1;
}}

/* ── Profession title ────────────────────────────────── */
/* اسم المهنة: NotoNaskh (Aniq بديل) — 13+5=18pt لكن كعنوان صفحة 26pt */
.profession-title {{
  font-family: 'NotoNaskh', serif;
  font-size: 26pt;
  font-weight: bold;
  color: #049e9e;
  text-align: right;
  margin-bottom: 7mm;
  line-height: 1.15;
}}

/* ── Section ─────────────────────────────────────────── */
.section {{
  margin-bottom: 5mm;
}}

/* عنوان العنصر: NotoKufi (Droid Arabic Kufi) — 13pt = 11pt + 2 */
.section-heading {{
  font-family: 'NotoKufi', sans-serif;
  font-size: 13pt;
  font-weight: bold;
  color: #5e4360;
  text-align: right;
  margin-bottom: 1.5mm;
  line-height: 1.4;
}}

/* محتوى العنصر: NotoKufi — 11pt */
.section-body {{
  font-family: 'NotoKufi', sans-serif;
  font-size: 11pt;
  color: #023663;
  text-align: right;
  line-height: 1.85;
}}

/* عنوان فرعي h3 */
.section-body h3 {{
  font-family: 'NotoKufi', sans-serif;
  font-size: 11.5pt;
  font-weight: bold;
  color: #023663;
  margin-top: 3mm;
  margin-bottom: 1mm;
}}

.section-body p  {{ margin-bottom: 1.5mm; }}

.section-body ul,
.section-body ol {{
  padding-right: 6mm;
  margin-top: 1mm;
  margin-bottom: 1mm;
}}
.section-body li {{ margin-bottom: 1mm; line-height: 1.8; }}

.section-body a {{ color: #049e9e; text-decoration: none; }}
.section-body strong {{ font-weight: bold; color: #023663; }}

/* ── Tables ──────────────────────────────────────────── */
.section-body table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 9.5pt;
  margin-top: 2mm;
  color: #023663;
}}
.section-body th {{
  background: #023663;
  color: #ffffff;
  padding: 2mm 3mm;
  text-align: center;
  font-weight: bold;
  font-size: 9pt;
}}
.section-body td {{
  padding: 1.8mm 3mm;
  border: 1px solid #c8d8e8;
  text-align: center;
  vertical-align: middle;
}}
.section-body tr:nth-child(even) td {{ background: #f0f5fa; }}
"""

# ── Footer HTML ───────────────────────────────────────────────────────────────
footer_html = f"""<div class="page-footer">
  <div class="footer-teal-bar"></div>
  <div class="footer-inner">
    <div class="footer-handles">
      <a class="fh" href="{TIKTOK_URL}"><span class="fi">&#9654;</span>{TIKTOK_USERNAME}</a>
      <a class="fh" href="https://instagram.com/{INSTA_USERNAME}"><span class="fi">&#9678;</span>{INSTA_USERNAME}</a>
      <a class="fh" href="https://snapchat.com/add/{SNAP_USERNAME}"><span class="fi">&#9673;</span>{SNAP_USERNAME}</a>
      <a class="fh" href="{X_URL}"><span class="fi">&#x1D54F;</span>{X_USERNAME}</a>
      <a class="fh" href="https://youtube.com/@{YT_USERNAME}"><span class="fi">&#9654;</span>{YT_USERNAME}</a>
      <a class="fh" href="{WEBSITE_URL}"><span class="fi">&#9678;</span>{WEBSITE}</a>
    </div>
    <div class="footer-arrow">&#10095;</div>
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
