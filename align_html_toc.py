import re
import os

html_path = "/home/dhakshin-raghav/projects/pre-booking-system/project_report.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. We must align the TOC, LOT, LOF tables to match the requested look
# In the reference, CHAPTER NO column is narrower, TITLE column is indented inside.
# TABLE OF CONTENTS table alignment modification:
toc_css = """
      <table style="border:none; width: 100%;">
        <tr style="border:none;">
          <th style="border:none; text-align:left; width:15%; font-weight:bold;">CHAPTER NO.</th>
          <th style="border:none; text-align:left; width:70%; font-weight:bold; padding-left: 20px;">TITLE</th>
          <th style="border:none; text-align:right; font-weight:bold;">PAGE NO.</th>
        </tr>
"""

# Let's replace the TOC table header block globally in the HTML
html = re.sub(
    r'<table style="border:none; width: 100%;">\s*<tr style="border:none;">\s*<th style="border:none; text-align:left; width:15%; font-weight:bold;">CHAPTER.*?</tr>',
    toc_css.strip(),
    html,
    flags=re.DOTALL
)

# Replace all the rows in TOC to have padding on the Title cell
html = re.sub(
    r'(<td style="border:none;)( text-align:left;">.*?</td>)',
    r'\1 padding-left: 20px;\2',
    html
)

# Apply same for LOT and LOF
html = re.sub(
    r'<th style="border:none; text-align:left; font-weight:bold;">TITLE</th>',
    r'<th style="border:none; text-align:left; font-weight:bold; padding-left: 20px;">TITLE</th>',
    html
)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated HTML table alignment to match reference layout.")
