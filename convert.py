import markdown

html_template = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Minor Project Report</title>
<style>
    body {{ font-family: 'Times New Roman', serif; font-size: 14pt; line-height: 1.6; max-width: 21cm; margin: 0 auto; padding: 2cm; background: white; }}
    h1, h2, h3 {{ text-align: center; }}
    h1 {{ font-size: 24pt; margin-top: 20px; margin-bottom: 20px;}}
    h2 {{ font-size: 20pt; margin-top: 30px; margin-bottom: 15px;}}
    h3 {{ font-size: 16pt; margin-top: 20px;}}
    p, li {{ text-align: justify; }}
    .page-break {{ page-break-before: always; }}
    @media print {{
        body {{ padding: 0; margin: 0; max-width: 100%; }}
        .page-break {{ page-break-before: always; }}
    }}
</style>
</head>
<body>
{content}
<script>
    setTimeout(function() { window.print(); }, 1000);
</script>
</body>
</html>"""

try:
    with open('D:\\travele\\Minor_Project_Report.md', 'r', encoding='utf-8') as f:
        text = f.read()

    text = text.replace('<div style="page-break-after: always;"></div>', '<div class="page-break"></div>')
    html_content = markdown.markdown(text)
    
    final_html = html_template.replace('{content}', html_content)
    
    with open('D:\\travele\\Minor_Project_Report.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    print("Success")
except Exception as e:
    print("Error:", e)
