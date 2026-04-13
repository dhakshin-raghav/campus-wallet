import fitz
import re
import subprocess
import os

pdf_path = "/home/dhakshin-raghav/projects/pre-booking-system/cafeteria_project_report.pdf"
html_path = "/home/dhakshin-raghav/projects/pre-booking-system/project_report.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Forcefully add Table 3.2 label if it was missed
if "Table 3.2" not in html and "Customer App Database Schema" in html:
    html = html.replace('Customer App Database Schema</h4>', 
        'Customer App Database Schema</h4>\n    <p style="text-align:center; font-style:italic;">Table 3.2: Customer App Database Schema</p>')
    # We must also add it to the LIST OF TABLES HTML block!
    lot_idx = html.find('<td style="border:none;">4.1</td>')
    if lot_idx != -1:
        # insert before 4.1
        insert_str = """
      <tr style="border:none;">
        <td style="border:none;">3.2</td>
        <td style="border:none; text-align:left;">Customer App Database Schema</td>
        <td style="border:none; text-align:right;">XX</td>
      </tr>"""
        html = html[:lot_idx] + insert_str + html[lot_idx:]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# 1. Re-render to get exact text flow
subprocess.run([
    "google-chrome", "--headless", "--no-sandbox", "--no-pdf-header-footer",
    "--print-to-pdf=" + pdf_path,
    "file://" + html_path
], check=True)

# 2. Extract boundaries
doc = fitz.open(pdf_path)

chap1_index = -1
for i in range(len(doc)):
    text = doc[i].get_text()
    if "CHAPTER 1" in text and "INTRODUCTION" in text:
        chap1_index = i
        break

print(f"CHAPTER 1 starts at {chap1_index}")

# We now map every Chapter, Table, and Figure to its Arabic/Roman page string
page_map = {}
roman_map = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii']

for i in range(2, chap1_index):
    page_map[i] = roman_map[i-1] # Wait, cover is 0. So Bonafide is 1?
    # Our doc has one cover page now! 
    # Physical 0 = Cover
    # Physical 1 = Bonafide
    # Physical 2 = Declaration
    # Physical 3 = Acknowledgement
    # Physical 4 = Abstract
    # Physical 5 = TOC
    
    # Let's fix the logic based on 1 cover page:
    pass

# Recalculate Frontmatter cleanly:
# 0: Cover
# 1..chap1_index-1: Frontmatter

roman_pg_map = {}
for i in range(1, chap1_index):
    roman_str = roman_map[i] # i=1 -> 'ii'? Usually cover is i. 
    # Let's say Bonafide is 'ii'
    roman_pg_map[i] = roman_str

arabic_pg_map = {}
for i in range(chap1_index, len(doc)):
    arabic_pg_map[i] = str(i - chap1_index + 1)

# Combine maps
full_page_map = {**roman_pg_map, **arabic_pg_map}

element_found = {}

for i in range(1, chap1_index):
    text = doc[i].get_text().replace('\n', ' ')
    pg_str = full_page_map[i]
    
    # Frontmatter
    if "TABLE OF CONTENTS" in text and "TOC" not in element_found: element_found["TABLE OF CONTENTS"] = pg_str
    if "LIST OF TABLES" in text and "LOT" not in element_found: element_found["LIST OF TABLES"] = pg_str
    if "LIST OF FIGURES" in text and "LOF" not in element_found: element_found["LIST OF FIGURES"] = pg_str

for i in range(chap1_index, len(doc)):
    text = doc[i].get_text().replace('\n', ' ')
    pg_str = full_page_map[i]
    
    # Chapters
    if "CHAPTER 1" in text and "INTRODUCTION" in text and "1" not in element_found: element_found["1"] = pg_str
    if "Background and Motivation" in text and "1.1" not in element_found: element_found["1.1"] = pg_str
    if "Role of Technology in Campus" in text and "1.2" not in element_found: element_found["1.2"] = pg_str
    if "Problem Statement" in text and "1.3" not in element_found: element_found["1.3"] = pg_str
    if "Scope of the Project" in text and "1.4" not in element_found: element_found["1.4"] = pg_str
    if "Organization of the Report" in text and "1.5" not in element_found: element_found["1.5"] = pg_str
    if "CHAPTER 2" in text and "LITERATURE SURVEY" in text and "2" not in element_found: element_found["2"] = pg_str
    if "Existing Systems and Approaches" in text and "2.1" not in element_found: element_found["2.1"] = pg_str
    if "Digital Ordering and Food-Tech" in text and "2.2" not in element_found: element_found["2.2"] = pg_str
    if "Campus Payment Systems" in text and "2.3" not in element_found: element_found["2.3"] = pg_str
    if "Real-Time Communication Patterns" in text and "2.4" not in element_found: element_found["2.4"] = pg_str
    
    # Tables and Figures
    # Look for "Table X.Y" or "Fig X.Y" in text.
    # Text is messy, let's use regex
    for t_m in re.finditer(r'Table\s+(\d+\.\d+)', text):
        t_id = t_m.group(1)
        key = f"Table_{t_id}"
        if key not in element_found: element_found[key] = pg_str
        
    for f_m in re.finditer(r'Fig(?:ure)?\s+(\d+\.\d+)', text):
        f_id = f_m.group(1)
        key = f"Fig_{f_id}"
        if key not in element_found: element_found[key] = pg_str

print("Elements mapped:", element_found)

# Write to HTML
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Update Chapters in TOC
for ch in ["1", "1.1", "1.2", "1.3", "1.4", "1.5", "2", "2.1", "2.2", "2.3", "2.4"]:
    if ch in element_found:
        pg = element_found[ch]
        pattern = r'(<td[^>]*>\s*' + re.escape(ch) + r'\s*</td>\s*<td[^>]*>.*?</td>\s*<td[^>]*>)\s*[A-Za-z0-9]+\s*(</td>)'
        html = re.sub(pattern, r'\g<1>' + str(pg) + r'\2', html, flags=re.DOTALL)

# Update Frontmatter in TOC
for lbl in ["TABLE OF CONTENTS", "LIST OF TABLES", "LIST OF FIGURES"]:
    if lbl in element_found:
        pg = element_found[lbl]
        pattern = r'(<td[^>]*>)\s*(' + re.escape(lbl) + r')\s*(</td>\s*<td[^>]*>)\s*[A-Za-z0-9]+\s*(</td>)'
        html = re.sub(pattern, r'\g<1>\g<2>\g<3>' + str(pg) + r'\g<4>', html, flags=re.DOTALL)

# Update Tables/Figures in their respective indices
for key, pg in element_found.items():
    if key.startswith("Table_"):
        t_id = key.split("_")[1]
        pattern = r'(<td[^>]*>\s*' + re.escape(t_id) + r'\s*</td>\s*<td[^>]*>.*?</td>\s*<td[^>]*>)\s*(?:XX|[A-Za-z0-9]+)\s*(</td>)'
        html = re.sub(pattern, r'\g<1>' + str(pg) + r'\2', html, flags=re.DOTALL)
    elif key.startswith("Fig_"):
        f_id = key.split("_")[1]
        pattern = r'(<td[^>]*>\s*' + re.escape(f_id) + r'\s*</td>\s*<td[^>]*>.*?</td>\s*<td[^>]*>)\s*(?:XX|[A-Za-z0-9]+)\s*(</td>)'
        html = re.sub(pattern, r'\g<1>' + str(pg) + r'\2', html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
    
print("Re-rendering PDF with final matched indices...")
# 3. Re-render
subprocess.run([
    "google-chrome", "--headless", "--no-sandbox", "--no-pdf-header-footer",
    "--print-to-pdf=" + pdf_path,
    "file://" + html_path
], check=True)

# 4. Stamp
doc = fitz.open(pdf_path)

for i in range(1, len(doc)):
    page = doc[i]
    rect = page.rect
    text = full_page_map.get(i, "")
    
    text_rect = fitz.Rect(0, rect.height - 60, rect.width, rect.height - 30)
    page.insert_textbox(text_rect, text, fontsize=12, fontname="times-roman", align=1)

tmp_path = "/home/dhakshin-raghav/projects/pre-booking-system/cafeteria_project_report_tmp.pdf"
doc.save(tmp_path)
os.rename(tmp_path, pdf_path)
print("Finished!")
