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
INSTA_URL       = f"https://instagram.com/{INSTA_USERNAME}"
YT_URL          = f"https://www.youtube.com/@{YT_USERNAME}"
WEBSITE_URL     = f"https://{WEBSITE}"

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
REPO_DIR  = os.path.dirname(os.path.dirname(BASE_DIR))
MD_FILE   = os.path.join(REPO_DIR, "outputs", "test_card_001_qadi.md")
LOGO_FILE = os.path.join(REPO_DIR, "design_reference", "tawjeeh_logo.jpeg")
FONTS_DIR = os.path.join(REPO_DIR, "design_reference", "fonts")
HTML_OUT  = os.path.join(BASE_DIR, "test_card_001_qadi.html")
PDF_OUT   = os.path.join(BASE_DIR, "test_card_001_qadi.pdf")

# ── Embed logo as base64 ──────────────────────────────────────────────────────
with open(LOGO_FILE, "rb") as f:
    LOGO_B64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()

# ── Footer platform icons (minimal inline SVGs, white strokes) ───────────────
def _svg_data_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

_SVG_STROKE = 'fill="none" stroke="#ffffff" stroke-width="2.9" stroke-linecap="round" stroke-linejoin="round"'

# نوتة موسيقية مفردة بخط أعرض — تبقى مفهومة بوضوح حتى عند التصغير
ICON_TIKTOK = _svg_data_uri(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {_SVG_STROKE}>'
    f'<circle cx="8.5" cy="17" r="3.1"/><path d="M11.6 17V4.5h2.4c.4 2.4 2.1 4 4.6 4.4"/></svg>'
)
# كاميرا مبسطة: جسم + عدسة دائرية فقط — أوضح بكثير عند الحجم الصغير
ICON_INSTAGRAM = _svg_data_uri(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {_SVG_STROKE}>'
    f'<rect x="3" y="6" width="18" height="13" rx="3"/>'
    f'<circle cx="12" cy="12.5" r="3.6"/>'
    f'<circle cx="16.6" cy="9.3" r="0.35" fill="#ffffff" stroke="none"/></svg>'
)
# مستطيل + مثلث تشغيل ممتلئ بنسب أكبر وأوضح — رمز يوتيوب الكلاسيكي
ICON_YOUTUBE = _svg_data_uri(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {_SVG_STROKE}>'
    f'<rect x="2.6" y="5.3" width="18.8" height="13.4" rx="3.6"/>'
    f'<path d="M9.8 9l6 3-6 3z" fill="#ffffff" stroke="none"/></svg>'
)
# كرة أرضية مبسطة: دائرة + خط استواء + خط طول واحد فقط — وضوح أعلى من الشكل المعقد سابقًا
ICON_WEB = _svg_data_uri(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {_SVG_STROKE}>'
    f'<circle cx="12" cy="12" r="8.2"/>'
    f'<path d="M3.8 12h16.4M12 3.8c2.6 2.2 2.6 14.2 0 16.4"/></svg>'
)

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
  margin: 0;
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

/* عنصر بسيط: أيقونة دائرية خفيفة + نص — بلا خلفية كبسولة ثقيلة */
.footer-link {{
  display: flex;
  align-items: center;
  gap: 1.8mm;
  flex: 0 0 auto;
}}

/* فاصل عمودي رفيع جدًا وهادئ بلون تركوازي متناسق مع الطرف الأخضر من التدرج */
.footer-divider {{
  flex: 0 0 auto;
  width: 0.25mm;
  height: 3.6mm;
  background: rgba(150, 235, 218, 0.22);
}}

.footer-icon {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 4.7mm;
  height: 4.7mm;
  flex-shrink: 0;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.16);
  background-repeat: no-repeat;
  background-position: center;
  background-size: 2.7mm 2.7mm;
  border: 0.3mm solid rgba(255, 255, 255, 0.7);
  color: #ffffff;
  font-weight: 700;
  font-size: 5pt;
  line-height: 1;
  overflow: hidden;
}}

.footer-text {{
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.4mm;
  overflow: hidden;
}}

.footer-platform {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  color: #ffffff;
  font-weight: 400;
  font-size: 4.3pt;
  letter-spacing: 0.3pt;
  opacity: 0.82;
}}

.footer-link a {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  color: #ffffff;
  font-size: 7.4pt;
  font-weight: 700;
  letter-spacing: 0.15pt;
  text-decoration: none;
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
.profession-title {{
  font-family: 'Aniq', 'Noto Naskh Arabic', serif;
  font-size: 17pt;
  font-weight: bold;
  color: #049e9e;
  text-align: right;
  margin-bottom: 7mm;
  line-height: 1.25;
}}

/* ── Section: تدفق ذكي — لا حبس للكتلة كاملة، العنوان يبقى مع بداية محتواه ── */
.section {{
  margin-bottom: 5mm;
  break-inside: auto;
  page-break-inside: auto;
}}

/* لا يُترك العنوان وحيدًا في آخر الصفحة — يبقى ملتصقًا بأول أسطر محتواه */
.section-heading {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  font-size: 12pt;
  font-weight: bold;
  color: #5e4360;
  text-align: right;
  margin-bottom: 1.5mm;
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
  line-height: 1.85;
  break-inside: auto;
  page-break-inside: auto;
}}

/* عنوان فرعي h3 (مثل: القطاع الحكومي) — قصير، يبقى مع أول سطر يليه دون فصل مشوه */
.section-body h3 {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  font-size: 10.5pt;
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
  <div class="footer-inner">
    <span class="footer-link"><span class="footer-icon" style="background-image:url('{ICON_TIKTOK}')"></span><span class="footer-text"><span class="footer-platform">TikTok</span><a href="{TIKTOK_URL}">{TIKTOK_USERNAME}</a></span></span>
    <span class="footer-divider"></span>
    <span class="footer-link"><span class="footer-icon">X</span><span class="footer-text"><span class="footer-platform">X</span><a href="{X_URL}">{X_USERNAME}</a></span></span>
    <span class="footer-divider"></span>
    <span class="footer-link"><span class="footer-icon" style="background-image:url('{ICON_INSTAGRAM}')"></span><span class="footer-text"><span class="footer-platform">Instagram</span><a href="{INSTA_URL}">{INSTA_USERNAME}</a></span></span>
    <span class="footer-divider"></span>
    <span class="footer-link"><span class="footer-icon" style="background-image:url('{ICON_YOUTUBE}')"></span><span class="footer-text"><span class="footer-platform">YouTube</span><a href="{YT_URL}">{YT_USERNAME}</a></span></span>
    <span class="footer-divider"></span>
    <span class="footer-link"><span class="footer-icon" style="background-image:url('{ICON_WEB}')"></span><span class="footer-text"><span class="footer-platform">Web</span><a href="{WEBSITE_URL}">{WEBSITE}</a></span></span>
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
