"""
صفحة اختبار بصرية لعنصر "الملاحظات المهنية المتقدمة"
مهنة الاختبار: قاضي
الهدف: مراجعة الشكل والقيمة فقط — المحتوى غير نهائي
"""
import os, base64
from weasyprint import HTML

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
REPO_DIR  = os.path.dirname(os.path.dirname(BASE_DIR))
LOGO_FILE = os.path.join(REPO_DIR, "design_reference", "project_logo_watermark_transparent.png")
FONTS_DIR = os.path.join(REPO_DIR, "design_reference", "fonts")
HTML_OUT  = os.path.join(BASE_DIR, "test_advanced_notes_display.html")
PDF_OUT   = os.path.join(BASE_DIR, "test_advanced_notes_display.pdf")

with open(LOGO_FILE, "rb") as f:
    LOGO_B64 = "data:image/png;base64," + base64.b64encode(f.read()).decode()

def svg_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

ST = 'fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"'
ICON_X      = svg_uri('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#000000" stroke="none"><path d="M5.2 4.6h3.1l3.7 4.9 4-4.9h2.8L13.6 11l5.4 8.4h-3.1l-4-5.3-4.4 5.3H4.6l5.9-7.2z"/></svg>')
ICON_TIKTOK = svg_uri('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#000000" stroke="none"><circle cx="9" cy="16.3" r="3.4"/><path d="M12.4 3.6h2.7c.3 2.5 2 4.3 4.5 4.6v2.7c-1.7 0-3.2-.5-4.5-1.4v6.8c0 .2 0 .4-.1.6h-2.6c0-.2.1-.4.1-.6V3.6z"/></svg>')
ICON_INSTA  = svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {ST}><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4.2"/></svg>')
ICON_SNAP   = svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {ST}><path d="M12 4c2.4 0 4 1.9 4 4.4 0 1.6.1 3 .9 3.9.6.6 1.3.8 2 1-.4.9-1.5 1.3-2.5 1.5 0 .6-.2 1.2-.7 1.2s-1-.3-1.7-.3c-.9 0-1.5.9-2 .9s-1.1-.9-2-.9c-.7 0-1.2.3-1.7.3s-.7-.6-.7-1.2c-1-.2-2.1-.6-2.5-1.5.7-.2 1.4-.4 2-1 .8-.9.9-2.3.9-3.9C8 5.9 9.6 4 12 4z"/></svg>')
ICON_YT     = svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {ST}><rect x="3" y="5.5" width="18" height="13" rx="3.5"/><path d="M10 9.3l5.2 2.7-5.2 2.7z" fill="#ffffff" stroke="none"/></svg>')
ICON_WEB    = svg_uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {ST}><circle cx="12" cy="12" r="8.2"/><path d="M3.8 12h16.4M12 3.8c2.6 2.2 2.6 14.2 0 16.4"/></svg>')

# ── الملاحظات الخمس — مهنة قاضي (نسخة مصححة) ──────────────────────────────
# المصدر: نظام القضاء السعودي ولوائحه — لا افتراض إعلانات أو مفاضلات غير منشورة.
# كل ملاحظة مبنية على نص نظامي أو هيكل تنظيمي رسمي.
NOTES = [
    # القيد النظامي — مصدر: نظام القضاء الصادر بالمرسوم الملكي م/64 لعام 1395هـ
    "نظام القضاء السعودي يشترط أن يكون القاضي سعودي الجنسية وأن يكون من أهل الكفاءة في الفقه الإسلامي؛ "
    "هذا يعني أن شهادات الحقوق أو القانون المدني دون رصيد شرعي كافٍ لا تُهيّئ مباشرة للسلك القضائي، "
    "وهو قيد نظامي يختلف عن شروط الجهات العدلية الأخرى.",

    # الفرق بين المسارات العدلية — مصدر: اللوائح التنظيمية لكل جهة
    "السلك القضائي وديوان المظالم والنيابة العامة ثلاثة مسارات عدلية مستقلة هيكليًا؛ "
    "التعيين في أحدها لا يُحتسب تلقائيًا مؤهلًا للانتقال لمسار آخر، "
    "وكل مسار له درجات وظيفية وآليات ترقية منفصلة بحسب نظامه الخاص.",

    # الملازمة كمتطلب تشغيلي — مصدر: لائحة التأهيل القضائي
    "الملازمة القضائية شرط تشغيلي لازم قبل الممارسة المستقلة، وليست مجرد فترة تدريب اختيارية؛ "
    "القاضي المعيَّن حديثًا يعمل تحت إشراف رسمي في مرحلة محددة قبل إسناد قضايا إليه منفردًا.",

    # المحاكم التجارية — مصدر: نظام المحاكم التجارية الصادر عام 1441هـ
    "إنشاء المحاكم التجارية المستقلة عام 1441هـ أوجد دوائر قضائية متخصصة بمنازعات الأعمال والشركات؛ "
    "هذا التخصص أفرز مسارًا قضائيًا مستقلًا لم يكن موجودًا في البنية التقليدية للمحاكم العامة.",

    # الفجوة بين الاشتراط الأكاديمي والتشغيلي — مصدر: نظام القضاء واللوائح التنفيذية
    "نظام القضاء يحدد الحد الأدنى للمؤهل الأكاديمي، لكن اللوائح التنفيذية تضيف اشتراطات تشغيلية "
    "تشمل اجتياز الاختبارات التحريرية والشفهية التي تُقيس الكفاءة الفقهية والإجرائية فعليًا.",
]

def build_list():
    items = []
    for note in NOTES:
        items.append(f'<li>{note}</li>')
    return "\n".join(items)

HTML_CONTENT = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<style>
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

@page {{
  size: A4;
  margin-top: 17mm;
  margin-right: 0;
  margin-bottom: 0;
  margin-left: 0;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body {{
  direction: rtl;
  font-family: 'Noto Kufi Arabic', sans-serif;
  background: #ffffff;
  color: #023663;
}}

/* ── Watermark ── */
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

/* ── Footer ── */
.footer {{
  position: fixed;
  left: 0; right: 0; bottom: 0;
  width: 100%; height: 12.5mm;
  background: linear-gradient(90deg, #023e96 0%, #017593 50%, #01b68e 100%);
  z-index: 999;
  overflow: hidden;
}}
.footer::before {{
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; height: 45%;
  background: linear-gradient(180deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0) 100%);
  pointer-events: none;
}}
.footer-inner {{
  position: relative;
  height: 12mm; width: 100%;
  padding: 0 14mm;
  display: flex;
  align-items: center;
  justify-content: space-between;
  direction: ltr;
}}
.footer-link {{
  display: flex; align-items: center; gap: 1.5mm; flex: 0 0 auto;
}}
.footer-icon {{
  display: inline-block; width: 3.5mm; height: 3.5mm;
  flex-shrink: 0;
  background-repeat: no-repeat; background-position: center; background-size: contain;
}}
.footer-icon-on-light {{
  width: 2.6mm; height: 2.6mm; border-radius: 50%;
  background-color: rgba(255,255,255,0.78);
  background-size: 1.9mm 1.9mm; padding: 0.45mm; box-sizing: content-box;
}}
.footer-link a {{
  font-family: 'Noto Kufi Arabic', sans-serif;
  color: #ffffff; font-size: 7.8pt; font-weight: 700;
  text-decoration: none;
  text-shadow: 0 0.2mm 0.3mm rgba(0,0,0,0.22);
}}
.footer-divider {{
  flex: 0 0 auto; width: 0.3mm; height: 6mm;
  background: rgba(120,235,210,0.45); border-radius: 0.2mm;
}}

/* ── Content ── */
.content {{
  position: relative;
  z-index: 1;
  padding: 0 17mm 32mm 17mm;
}}

.page-label {{
  font-size: 7.5pt;
  color: #8a9aaa;
  text-align: center;
  margin-bottom: 5mm;
  letter-spacing: 0.3pt;
}}

.section-heading {{
  font-size: 12pt;
  font-weight: bold;
  color: #5e4360;
  text-align: right;
  margin-bottom: 4mm;
  line-height: 1.4;
}}

/* ── Notes list ── */
.notes-list {{
  list-style: disc;
  list-style-position: outside;
  padding-right: 5mm;
  padding-left: 0;
}}

.notes-list li {{
  font-size: 10pt;
  line-height: 1.75;
  margin-bottom: 3.5mm;
  color: #023663;
  break-inside: avoid-page;
}}

.notes-list li::marker {{
  color: #023663;
  font-size: 1.35em;
}}

.notes-list a {{
  color: #023663;
  text-decoration-line: underline;
  text-decoration-style: dotted;
  text-decoration-color: #023663;
  text-decoration-thickness: 0.3mm;
  text-underline-offset: 0.65mm;
}}

</style>
</head>
<body>

<img class="page-watermark" src="{LOGO_B64}" alt="">

<div class="content">
  <p class="page-label">صفحة اختبار بصري — شكل وقيمة فقط — المحتوى غير نهائي — مهنة: قاضي</p>

  <div class="section-heading">الملاحظات المهنية المتقدمة</div>

  <ul class="notes-list">
{build_list()}
  </ul>
</div>

<!-- Footer -->
<div class="footer">
  <div class="footer-inner">
    <div class="footer-link">
      <div class="footer-icon footer-icon-on-light" style="background-image:url('{ICON_X}')"></div>
      <a href="https://x.com/tawjeeh_hub">tawjeeh_hub</a>
    </div>
    <div class="footer-divider"></div>
    <div class="footer-link">
      <div class="footer-icon footer-icon-on-light" style="background-image:url('{ICON_TIKTOK}')"></div>
      <a href="https://www.tiktok.com/@tawjeeh.hub">tawjeeh.hub</a>
    </div>
    <div class="footer-divider"></div>
    <div class="footer-link">
      <div class="footer-icon" style="background-image:url('{ICON_INSTA}')"></div>
      <a href="https://instagram.com/tawjeeh.hub">tawjeeh.hub</a>
    </div>
    <div class="footer-divider"></div>
    <div class="footer-link">
      <div class="footer-icon" style="background-image:url('{ICON_SNAP}')"></div>
      <a href="https://www.snapchat.com/add/tawjeeh.hub">tawjeeh.hub</a>
    </div>
    <div class="footer-divider"></div>
    <div class="footer-link">
      <div class="footer-icon" style="background-image:url('{ICON_YT}')"></div>
      <a href="https://www.youtube.com/@tawjeeh_hub">tawjeeh_hub</a>
    </div>
    <div class="footer-divider"></div>
    <div class="footer-link">
      <div class="footer-icon" style="background-image:url('{ICON_WEB}')"></div>
      <a href="https://www.tawjeeh.hub">www.tawjeeh.hub</a>
    </div>
  </div>
</div>

</body>
</html>"""

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)
print(f"HTML: {HTML_OUT}")

HTML(string=HTML_CONTENT, base_url=BASE_DIR).write_pdf(PDF_OUT)
print(f"PDF:  {PDF_OUT}")
