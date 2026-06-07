import markdown
import re
import os
import base64
from weasyprint import HTML

# ── Social handles ────────────────────────────────────────────────────────────
X_USERNAME      = "tawjeeh_hub"
TIKTOK_USERNAME = "tawjeeh_hub"
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
                    f'<div class="section">'
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
  margin: 0;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body {{
  direction: rtl;
  font-family: 'NotoKufi', sans-serif;
  background: #ffffff;
  color: #023663;
}}

/* عدم ترك عنوان أو سطر معزول عند تقسيم الصفحات */
p, li, td, th {{
  orphans: 2;
  widows: 2;
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

/* ── Fixed footer — identity bar, edge-to-edge on every page ── */
.footer {{
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 11mm;
  background: #023663;
  box-sizing: border-box;
  z-index: 999;
  overflow: hidden;
}}

.footer-teal-bar {{
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  height: 1.2mm;
  background: #049e9e;
}}

.footer-inner {{
  position: relative;
  height: 11mm;
  margin: 0 7mm;
  padding: 1.2mm 8mm 0 8mm;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  direction: rtl;
}}

.footer-brand {{
  color: #ffffff;
  font-size: 7pt;
  font-weight: 600;
  white-space: nowrap;
  direction: ltr;
  unicode-bidi: isolate;
}}

.footer-links {{
  display: flex;
  align-items: center;
  gap: 2.2mm;
  direction: ltr;
  white-space: nowrap;
}}

.footer-link {{
  display: inline-flex;
  align-items: center;
  gap: 1mm;
  font-size: 5.8pt;
  font-weight: 400;
  line-height: 1;
}}

.footer-platform {{
  color: #049e9e;
  font-weight: 500;
}}

.footer-link a {{
  font-family: 'NotoKufi', sans-serif;
  color: #ffffff;
  text-decoration: none;
  opacity: 0.95;
}}

.footer-divider {{
  width: 0.3mm;
  height: 3mm;
  background: #049e9e;
  opacity: 0.65;
  display: inline-block;
}}

/* ── Main content ────────────────────────────────────── */
.content {{
  position: relative;
  z-index: 1;
  box-sizing: border-box;
  /* الهوامش انتقلت هنا بعد إلغاء هوامش @page لإتاحة Footer ممتد للحواف */
  padding: 18mm 18mm 24mm 18mm;
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

/* ── Section: تدفق ذكي — لا حبس للكتلة كاملة، العنوان يبقى مع بداية محتواه ── */
.section {{
  margin-bottom: 5mm;
  break-inside: auto;
  page-break-inside: auto;
}}

/* عنوان العنصر: NotoKufi (Droid Arabic Kufi) — 13pt = 11pt + 2 */
/* لا يُترك العنوان وحيدًا في آخر الصفحة — يبقى ملتصقًا بأول أسطر محتواه */
.section-heading {{
  font-family: 'NotoKufi', sans-serif;
  font-size: 13pt;
  font-weight: bold;
  color: #5e4360;
  text-align: right;
  margin-bottom: 1.5mm;
  line-height: 1.4;
  break-after: avoid;
  page-break-after: avoid;
}}

/* محتوى العنصر: NotoKufi — 11pt — يتدفق بحرية بين الصفحات */
.section-body {{
  font-family: 'NotoKufi', sans-serif;
  font-size: 11pt;
  color: #023663;
  text-align: right;
  line-height: 1.85;
  break-inside: auto;
  page-break-inside: auto;
}}

/* عنوان فرعي h3 (مثل: القطاع الحكومي) — قصير، يبقى مع أول سطر يليه دون فصل مشوه */
.section-body h3 {{
  font-family: 'NotoKufi', sans-serif;
  font-size: 11.5pt;
  font-weight: bold;
  color: #023663;
  margin-top: 3mm;
  margin-bottom: 1mm;
  break-after: avoid;
  page-break-after: avoid;
}}

.section-body p  {{
  margin-bottom: 1.5mm;
  break-inside: avoid-page;
}}

.section-body ul,
.section-body ol {{
  padding-right: 6mm;
  margin-top: 1mm;
  margin-bottom: 1mm;
}}
.section-body li {{
  margin-bottom: 1mm;
  line-height: 1.8;
  break-inside: avoid-page;
}}

.section-body a {{ color: #049e9e; text-decoration: none; }}
.section-body strong {{ font-weight: bold; color: #023663; }}

/* ── Tables: تنقسم بشكل نظيف، رأس الجدول يتكرر ───────── */
.section-body table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 8.5pt;
  line-height: 1.55;
  margin-top: 2mm;
  color: #023663;
  break-inside: auto;
  page-break-inside: auto;
}}
.section-body thead {{
  display: table-header-group;
}}
.section-body tr {{
  break-inside: avoid;
  page-break-inside: avoid;
}}
.section-body th {{
  background: #023663;
  color: #ffffff;
  padding: 1.6mm 2.2mm;
  text-align: center;
  font-weight: bold;
  font-size: 8.5pt;
  vertical-align: middle;
}}
.section-body td {{
  padding: 1.6mm 2.2mm;
  border: 1px solid #c8d8e8;
  text-align: center;
  vertical-align: top;
}}
.section-body tr:nth-child(even) td {{ background: #f0f5fa; }}
"""

# ── Footer HTML ───────────────────────────────────────────────────────────────
footer_html = f"""<div class="footer">
  <div class="footer-teal-bar"></div>
  <div class="footer-inner">
    <div class="footer-brand">Tawjeeh HUB</div>
    <div class="footer-links">
      <span class="footer-link"><span class="footer-platform">X</span><a href="{X_URL}">{X_USERNAME}</a></span>
      <span class="footer-divider"></span>
      <span class="footer-link"><span class="footer-platform">TikTok</span><a href="{TIKTOK_URL}">{TIKTOK_USERNAME}</a></span>
      <span class="footer-divider"></span>
      <span class="footer-link"><span class="footer-platform">Instagram</span><a href="https://instagram.com/{INSTA_USERNAME}">{INSTA_USERNAME}</a></span>
      <span class="footer-divider"></span>
      <span class="footer-link"><span class="footer-platform">Web</span><a href="{WEBSITE_URL}">{WEBSITE}</a></span>
    </div>
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
