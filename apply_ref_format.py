import re

html_path = "/home/dhakshin-raghav/projects/pre-booking-system/project_report.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════════════════════════
# REFERENCE ANALYSIS RESULTS:
# ──────────────────────────────────────────────────────────────────────────────
# Font: Times New Roman, 14pt throughout
# Body text left margin: x=72pt
# First-line indent: x=108pt (i.e., 36pt = ~1.27cm indent on first line)
# Section headings (e.g. "2.4 Summary"): BOLD, at x=72 (no indent)
# Sub-section items in lists: x=108, bold lead term + regular description
# Figure/Table captions: BOLD, centered
# Chapter titles: BOLD, centered, larger
# ══════════════════════════════════════════════════════════════════════════════

# 1. Replace the font-family with Times New Roman and set base size to 14pt
old_body_css = """    body {
      max-width: 210mm;
      margin: 0 auto;
      padding: 25mm 25mm 25mm 30mm;
      font-family: 'Times New Roman', Georgia, serif;
      font-size: 12pt;
      line-height: 1.6;
      color: #000;
    }"""

new_body_css = """    body {
      max-width: 210mm;
      margin: 0 auto;
      padding: 25mm 25mm 25mm 30mm;
      font-family: 'Times New Roman', Georgia, serif;
      font-size: 14pt;
      line-height: 1.5;
      color: #000;
    }"""

html = html.replace(old_body_css, new_body_css)

# 2. Update paragraph styling: first-line indent of ~1.27cm (36pt), justified
old_p_css = """
    p {
      margin-bottom: 10px;
      text-align: justify;
      text-indent: 1.25cm;
    }
    .center, .cover-page p, .page-number, p.bold, th, td p {
      text-indent: 0 !important;
    }
"""

new_p_css = """
    p {
      margin-bottom: 8px;
      text-align: justify;
      text-indent: 1.27cm;
      line-height: 1.5;
    }
    .center, .cover-page p, .page-number, p.bold, th p, td p,
    p[style*="text-align:center"], p[style*="font-weight:bold"],
    .chapter-title + p, table + p, div[style*="border"] p {
      text-indent: 0 !important;
    }
"""

html = html.replace(old_p_css, new_p_css)

# 3. Update section headings to be bold (they should use <strong> or font-weight:bold)
# The reference has section numbers like "2.4 Summary of Challenges" in BOLD
# Our CSS class .section-heading should enforce bold
old_section_heading = """    .section-heading {
      font-size: 14pt;
      font-weight: bold;
      margin-top: 25px;
      margin-bottom: 10px;
    }"""

new_section_heading = """    .section-heading {
      font-size: 14pt;
      font-weight: bold;
      margin-top: 20px;
      margin-bottom: 8px;
      text-indent: 0 !important;
    }"""

html = html.replace(old_section_heading, new_section_heading)

# 4. Update sub-section headings
old_sub_section = """    .sub-section {
      font-size: 12pt;
      font-weight: bold;
      margin-top: 15px;
      margin-bottom: 8px;
    }"""

new_sub_section = """    .sub-section {
      font-size: 14pt;
      font-weight: bold;
      margin-top: 15px;
      margin-bottom: 8px;
      text-indent: 0 !important;
    }"""

html = html.replace(old_sub_section, new_sub_section)

# 5. Update chapter title styling
old_chapter_title = """    .chapter-title {
      text-align: center;
      font-size: 16pt;
      font-weight: bold;
      margin-bottom: 30px;
      padding-top: 30px;
    }"""

new_chapter_title = """    .chapter-title {
      text-align: center;
      font-size: 16pt;
      font-weight: bold;
      margin-bottom: 25px;
      padding-top: 20px;
      text-indent: 0 !important;
    }"""

html = html.replace(old_chapter_title, new_chapter_title)

# 6. Make figure/table captions bold and centered (matching reference)
# Find all figure captions and make them bold
# Pattern: <p style="text-align:center; font-style:italic;...">Fig X.Y...</p>
# Change to: <p style="text-align:center; font-weight:bold;...">
html = re.sub(
    r'(<p\s+style="[^"]*?)font-style:italic([^"]*?">\s*(?:Fig|Figure)\s+\d)',
    r'\1font-weight:bold\2',
    html
)

# Same for Table captions that use <em>
html = re.sub(
    r'<p\s+style="text-align:center;">\s*<em>(Table\s+\d)',
    r'<p style="text-align:center; font-weight:bold;">\1',
    html
)
html = re.sub(
    r'</em>\s*</p>',
    r'</p>',
    html
)

# Also make standalone table captions bold
html = re.sub(
    r'(<p\s+style="[^"]*?)font-style:italic([^"]*?">\s*Table\s+\d)',
    r'\1font-weight:bold\2',
    html
)

# 7. Update list items to use consistent indentation
# In the reference, list items at x=108 have bold lead terms
# Our HTML already uses <strong> for lead terms in <li>, which is correct
# Just need to ensure consistent list styling
old_li_css = """    li {
      margin-bottom: 5px;
    }"""
    
new_li_css = """    li {
      margin-bottom: 6px;
      text-align: justify;
      line-height: 1.5;
    }
    
    ul, ol {
      padding-left: 1.27cm;
      margin-bottom: 10px;
    }"""

if old_li_css in html:
    html = html.replace(old_li_css, new_li_css)
else:
    # Add before closing </style>
    style_end = html.find('</style>')
    if style_end != -1:
        li_css_inject = """
    li {
      margin-bottom: 6px;
      text-align: justify;
      line-height: 1.5;
    }
    
    ul, ol {
      padding-left: 1.27cm;
      margin-bottom: 10px;
    }
"""
        html = html[:style_end] + li_css_inject + html[style_end:]

# 8. Update table styling to match reference (14pt body, bold headers)
old_table_css = """    table {
      width: 100%;
      border-collapse: collapse;
      margin: 15px 0;
      font-size: 11pt;
    }"""

new_table_css = """    table {
      width: 100%;
      border-collapse: collapse;
      margin: 15px 0;
      font-size: 12pt;
    }"""

html = html.replace(old_table_css, new_table_css)

# 9. Ensure th (table headers) are bold
old_th_css = """    th {
      background-color: #f0f0f0;
      font-weight: bold;
      padding: 8px;
      border: 1px solid #000;
    }"""

new_th_css = """    th {
      background-color: #f0f0f0;
      font-weight: bold;
      padding: 8px;
      border: 1px solid #000;
      text-align: center;
    }"""

html = html.replace(old_th_css, new_th_css)

# 10. Update h2 styling (used for frontmatter titles like "TABLE OF CONTENTS")
old_h2 = """    h2 {
      font-size: 16pt;
      text-align: center;
      font-weight: bold;
    }"""

new_h2 = """    h2 {
      font-size: 16pt;
      text-align: center;
      font-weight: bold;
      text-indent: 0 !important;
    }"""

html = html.replace(old_h2, new_h2)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Applied reference formatting patterns:")
print("  - Times New Roman 14pt body text")
print("  - 1.27cm first-line paragraph indent")
print("  - Bold section & sub-section headings (no indent)")
print("  - Bold centered figure/table captions")
print("  - Justified text with 1.5 line spacing")
print("  - Consistent list indentation")
