import markdown
import re

with open('/home/user/tawjeeh-sharia-cards/outputs/test_card_001_qadi.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

html_body = markdown.markdown(
    md_content,
    extensions=['tables', 'nl2br'],
    output_format='html'
)

html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>بطاقة مهنة قاضي</title>
<style>
  @page {{
    size: A4;
    margin: 2cm 2.5cm;
  }}
  * {{
    box-sizing: border-box;
  }}
  body {{
    font-family: 'Arial', 'Tahoma', sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a1a;
    direction: rtl;
    text-align: right;
    background: white;
  }}
  h1 {{
    font-size: 18pt;
    font-weight: bold;
    color: #1a3a5c;
    border-bottom: 3px solid #1a3a5c;
    padding-bottom: 6px;
    margin-top: 0;
    margin-bottom: 16px;
  }}
  h2 {{
    font-size: 13pt;
    font-weight: bold;
    color: #1a3a5c;
    border-right: 4px solid #1a3a5c;
    padding-right: 8px;
    margin-top: 24px;
    margin-bottom: 10px;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 11pt;
    font-weight: bold;
    color: #2c5282;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }}
  p {{
    margin: 6px 0;
  }}
  ul {{
    padding-right: 20px;
    padding-left: 0;
    margin: 6px 0;
  }}
  li {{
    margin: 4px 0;
  }}
  ol {{
    padding-right: 20px;
    padding-left: 0;
    margin: 6px 0;
  }}
  ol li {{
    margin: 8px 0;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 9.5pt;
    page-break-inside: auto;
  }}
  th {{
    background-color: #1a3a5c;
    color: white;
    padding: 8px 10px;
    text-align: right;
    font-weight: bold;
    border: 1px solid #1a3a5c;
  }}
  td {{
    padding: 7px 10px;
    border: 1px solid #c8d8e8;
    vertical-align: top;
    text-align: right;
  }}
  tr:nth-child(even) td {{
    background-color: #f0f5fb;
  }}
  a {{
    color: #1a3a5c;
    text-decoration: underline;
  }}
  hr {{
    border: none;
    border-top: 1px solid #c8d8e8;
    margin: 16px 0;
  }}
  blockquote {{
    border-right: 3px solid #c8d8e8;
    padding-right: 12px;
    margin-right: 0;
    color: #444;
  }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

with open('/home/user/tawjeeh-sharia-cards/outputs/pdf/test_card_001_qadi.html', 'w', encoding='utf-8') as f:
    f.write(html)

from weasyprint import HTML, CSS
HTML(filename='/home/user/tawjeeh-sharia-cards/outputs/pdf/test_card_001_qadi.html').write_pdf(
    '/home/user/tawjeeh-sharia-cards/outputs/pdf/test_card_001_qadi.pdf'
)
print("PDF created successfully")
