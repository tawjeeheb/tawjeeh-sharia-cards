import markdown
import re
import os

with open('/home/user/tawjeeh-sharia-cards/outputs/test_card_001_qadi.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

H2_HEADINGS = {
    'المسميات المكافئة',
    'التصنيف الوطني SSC',
    'طبيعة العمل',
    'المهام الرئيسية',
    'المرتبة والراتب',
    'المزايا الوظيفية',
    'الشروط والمؤهلات',
    'متطلبات التقييم والتهيئة المهنية',
    'الخبرات المطلوبة',
    'برامج التأهيل المعتمدة',
    'الشهادات المهنية الاحترافية',
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
    'الجهات شبه الحكومية',
    'القطاع الحكومي',
    'القطاع شبه الحكومي',
    'القطاع الخاص',
    'القطاع غير الربحي',
    'القطاع المستقل',
    'العمل الحر',
    'السلك القضائي — وزارة العدل وديوان المظالم',
    'جهات سبق وأعلنت',
}

processed = []
for line in lines:
    stripped = line.rstrip()
    if re.match(r'^\d+\.\s+\S', stripped) and len(stripped) < 30:
        title = re.sub(r'^\d+\.\s+', '', stripped)
        processed.append(f'# {title}\n')
    elif stripped in H2_HEADINGS:
        processed.append(f'## {stripped}\n')
    elif stripped in H3_HEADINGS:
        processed.append(f'### {stripped}\n')
    else:
        processed.append(line)

md_content = ''.join(processed)

html_body = markdown.markdown(
    md_content,
    extensions=['tables', 'nl2br'],
    output_format='html'
)

# Wrap sections in styled cards
def wrap_sections(html_body):
    parts = re.split(r'(<h2>.*?</h2>)', html_body, flags=re.DOTALL)
    result = []

    if parts:
        first = parts[0].strip()
        h1_match = re.search(r'<h1>(.*?)</h1>', first, re.DOTALL)
        if h1_match:
            title = h1_match.group(1)
            result.append(f'''<div class="card-header">
  <div class="header-accent"></div>
  <div class="header-content">
    <div class="header-label">بطاقة مهنية</div>
    <h1>{title}</h1>
    <div class="header-sub">Tawjeeh HUB &nbsp;·&nbsp; منصة التوجيه المهني</div>
  </div>
</div>
<div class="content-area">''')
        else:
            result.append('<div class="content-area">')

    i = 1
    while i < len(parts):
        h2_tag = parts[i]
        body = parts[i+1].strip() if i+1 < len(parts) else ''
        result.append(f'''<div class="section-card">
  <div class="section-header">{h2_tag}</div>
  <div class="section-body">{body}</div>
</div>''')
        i += 2

    result.append('</div>')  # close content-area
    result.append('''<div class="card-footer">
  <span>Tawjeeh HUB</span>
  <span class="sep">·</span>
  <span>بطاقة مهنية — للاستخدام التجريبي فقط</span>
</div>''')
    return '\n'.join(result)

wrapped_body = wrap_sections(html_body)

css = """
@page {
  size: A4;
  margin: 0;
}
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Arial', 'Tahoma', sans-serif;
  font-size: 10pt;
  line-height: 1.8;
  color: #1c2b3a;
  direction: rtl;
  text-align: right;
  background: #f0f4f8;
}

/* ─── Page wrapper ─── */
.page-wrapper {
  width: 210mm;
  min-height: 297mm;
  background: #f0f4f8;
  margin: 0 auto;
}

/* ─── Header ─── */
.card-header {
  background: #023663;
  position: relative;
  overflow: hidden;
  padding: 0;
  display: flex;
  min-height: 90px;
}
.header-accent {
  width: 8px;
  background: #049e9e;
  flex-shrink: 0;
}
.header-content {
  padding: 20px 24px 18px 20px;
  flex: 1;
}
.header-label {
  font-size: 7.5pt;
  color: #049e9e;
  letter-spacing: 2px;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.card-header h1 {
  font-size: 26pt;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.1;
  margin: 0 0 6px 0;
}
.header-sub {
  font-size: 8pt;
  color: rgba(255,255,255,0.55);
  font-weight: 400;
}

/* ─── Content area ─── */
.content-area {
  padding: 16px 16px 8px 16px;
}

/* ─── Section cards ─── */
.section-card {
  background: #ffffff;
  border-radius: 6px;
  margin-bottom: 10px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.07);
  page-break-inside: avoid;
}

.section-header {
  background: #023663;
  padding: 0;
}
.section-header h2 {
  font-size: 10.5pt;
  font-weight: 700;
  color: #ffffff;
  padding: 7px 12px 7px 10px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  page-break-after: avoid;
}
.section-header h2::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 14px;
  background: #049e9e;
  border-radius: 2px;
  margin-left: 6px;
  flex-shrink: 0;
}

/* ─── Section body ─── */
.section-body {
  padding: 10px 14px 12px 14px;
}

.section-body h3 {
  font-size: 9.5pt;
  font-weight: 700;
  color: #023663;
  background: #e8f5f5;
  border-right: 3px solid #049e9e;
  padding: 4px 10px;
  margin: 10px 0 5px 0;
  border-radius: 0 4px 4px 0;
  page-break-after: avoid;
}

.section-body p {
  margin: 4px 0;
  font-size: 9.5pt;
  color: #2d3e50;
}

.section-body ul {
  padding-right: 18px;
  padding-left: 0;
  margin: 4px 0;
}
.section-body ul li {
  margin: 3px 0;
  font-size: 9.5pt;
  color: #2d3e50;
}
.section-body ol {
  padding-right: 18px;
  padding-left: 0;
  margin: 4px 0;
}
.section-body ol li {
  margin: 6px 0;
  font-size: 9.5pt;
  color: #2d3e50;
}

/* ─── Links ─── */
a {
  color: #049e9e;
  text-decoration: none;
  border-bottom: 1px dotted rgba(4,158,158,0.5);
}

/* ─── Tables ─── */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
  font-size: 8pt;
  border-radius: 4px;
  overflow: hidden;
  page-break-inside: auto;
}
thead { display: table-header-group; }
tr { page-break-inside: avoid; }

th {
  background: #023663;
  color: #ffffff;
  padding: 7px 9px;
  text-align: right;
  font-weight: 700;
  font-size: 8.5pt;
  border: none;
  border-left: 1px solid rgba(255,255,255,0.1);
}
th:last-child { border-left: none; }

td {
  padding: 6px 9px;
  border-bottom: 1px solid #e8eef4;
  border-left: 1px solid #e8eef4;
  vertical-align: top;
  text-align: right;
  font-size: 8pt;
  color: #2d3e50;
}
td:last-child { border-left: none; }
tr:last-child td { border-bottom: none; }
tr:nth-child(even) td { background: #f5fafc; }

/* ─── Footer ─── */
.card-footer {
  background: #023663;
  color: rgba(255,255,255,0.5);
  text-align: center;
  font-size: 7.5pt;
  padding: 8px;
  letter-spacing: 0.5px;
}
.card-footer .sep { margin: 0 6px; color: #049e9e; }
"""

html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>بطاقة مهنة قاضي — Tawjeeh HUB</title>
<style>
{css}
</style>
</head>
<body>
<div class="page-wrapper">
{wrapped_body}
</div>
</body>
</html>"""

out_dir = '/home/user/tawjeeh-sharia-cards/outputs/pdf'
with open(f'{out_dir}/test_card_001_qadi.html', 'w', encoding='utf-8') as f:
    f.write(html)

from weasyprint import HTML as WH
WH(filename=f'{out_dir}/test_card_001_qadi.html').write_pdf(
    f'{out_dir}/test_card_001_qadi.pdf'
)
doc = WH(filename=f'{out_dir}/test_card_001_qadi.html').render()
print(f'Pages: {len(doc.pages)}')
print(f'PDF size: {os.path.getsize(f"{out_dir}/test_card_001_qadi.pdf"):,} bytes')

# Verify all sections present
with open(f'{out_dir}/test_card_001_qadi.html', 'r', encoding='utf-8') as f:
    h = f.read()
sections = ['المسميات المكافئة','التصنيف الوطني','المرتبة والراتب','برامج التأهيل',
            'الشهادات المهنية','الدورات الداعمة','جهات التوظيف','الملاحظات المهنية',
            'النصائح العملية','جدول مدى قبول التخصصات']
all_present = all(s in h for s in sections)
print(f'All sections present: {all_present}')
print(f'SOURCES_LOG absent: {"SOURCES_LOG" not in h}')
print('Done')
