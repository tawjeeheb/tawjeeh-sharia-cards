import markdown
import re

with open('/home/user/tawjeeh-sharia-cards/outputs/test_card_001_qadi.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Known section headings (h2) and sub-headings (h3)
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
    # Title line: "1. قاضي"
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

html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>بطاقة مهنة قاضي</title>
<style>
  @page {
    size: A4;
    margin: 2cm 2.5cm;
  }
  * { box-sizing: border-box; }
  body {
    font-family: 'Arial', 'Tahoma', sans-serif;
    font-size: 10.5pt;
    line-height: 1.75;
    color: #1a1a1a;
    direction: rtl;
    text-align: right;
    background: white;
  }
  h1 {
    font-size: 20pt;
    font-weight: bold;
    color: #0d2b4e;
    border-bottom: 3px solid #0d2b4e;
    padding-bottom: 8px;
    margin-top: 0;
    margin-bottom: 20px;
    page-break-after: avoid;
  }
  h2 {
    font-size: 13pt;
    font-weight: bold;
    color: #ffffff;
    background-color: #1a3a5c;
    padding: 5px 10px;
    margin-top: 22px;
    margin-bottom: 10px;
    page-break-after: avoid;
  }
  h3 {
    font-size: 11pt;
    font-weight: bold;
    color: #1a3a5c;
    border-right: 4px solid #1a3a5c;
    padding-right: 8px;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }
  p { margin: 5px 0; }
  ul {
    padding-right: 18px;
    padding-left: 0;
    margin: 5px 0;
  }
  li { margin: 3px 0; }
  ol {
    padding-right: 18px;
    padding-left: 0;
    margin: 5px 0;
  }
  ol li { margin: 7px 0; }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 9pt;
    page-break-inside: auto;
  }
  thead { display: table-header-group; }
  tr { page-break-inside: avoid; }
  th {
    background-color: #1a3a5c;
    color: white;
    padding: 7px 9px;
    text-align: right;
    font-weight: bold;
    border: 1px solid #1a3a5c;
  }
  td {
    padding: 6px 9px;
    border: 1px solid #b8cfe0;
    vertical-align: top;
    text-align: right;
  }
  tr:nth-child(even) td { background-color: #f0f5fb; }
  a { color: #1a3a5c; text-decoration: underline; }
</style>
</head>
<body>
""" + html_body + """
</body>
</html>"""

with open('/home/user/tawjeeh-sharia-cards/outputs/pdf/test_card_001_qadi.html', 'w', encoding='utf-8') as f:
    f.write(html)

from weasyprint import HTML
HTML(filename='/home/user/tawjeeh-sharia-cards/outputs/pdf/test_card_001_qadi.html').write_pdf(
    '/home/user/tawjeeh-sharia-cards/outputs/pdf/test_card_001_qadi.pdf'
)
print("Done")
