import fitz
import re
import subprocess
import os

pdf_path = "/home/dhakshin-raghav/projects/pre-booking-system/cafeteria_project_report.pdf"
html_path = "/home/dhakshin-raghav/projects/pre-booking-system/project_report.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the 5.2.x -> 6.2.x
for i in range(1, 8):
    html = html.replace(f'5.2.{i}', f'6.2.{i}')

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

roman_map = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv']
roman_pg_map = {}
for i in range(1, chap1_index):
    roman_pg_map[i] = roman_map[i-1]

arabic_pg_map = {}
for i in range(chap1_index, len(doc)):
    arabic_pg_map[i] = str(i - chap1_index + 1)

full_page_map = {**roman_pg_map, **arabic_pg_map}
element_found = {}

chapter_searches = {
    "1": "CHAPTER 1", "1.1": "Background and Motivation", "1.2": "Role of Technology in Campus", 
    "1.3": "Problem Statement", "1.4": "Scope of the Project", "1.5": "Organization of the Report",
    "2": "LITERATURE SURVEY", "2.1": "Existing Systems and Approaches", "2.2": "Digital Ordering and Food-Tech",
    "2.3": "Gap Identification",
    "3": "SYSTEM DIAGRAMS AND DESIGN", "3.1": "General Objectives", "3.2": "System Architecture",
    "3.3": "Module Description", "3.4": "Tools and Technologies Used", "3.5": "Use Case Diagram",
    "4": "SYSTEM TESTING AND VALIDATION", "4.1": "System Implementation Results", "4.2": "API Endpoint Summary",
    "4.3": "Performance Analysis", "4.4": "Discussion of Results", "4.5": "Testing Methodology",
    "5": "CONTINUOUS INTEGRATION", "5.1": "Overview of CI/CD Methodology", "5.2": "GitHub Actions Architecture",
    "5.3": "Jenkins Pipeline as Code", "5.4": "Docker Containerization Strategy", "5.5": "AWS EC2 Deployment Architecture",
    "6": "CONCLUSION AND FUTURE", "6.1": "Conclusion", "6.2": "Future Works"
}

for i in range(1, chap1_index):
    text = doc[i].get_text().replace('\n', ' ')
    pg_str = full_page_map[i]
    if "TABLE OF CONTENTS" in text and "TOC" not in element_found: element_found["TABLE OF CONTENTS"] = pg_str
    if "LIST OF TABLES" in text and "LOT" not in element_found: element_found["LIST OF TABLES"] = pg_str
    if "LIST OF FIGURES" in text and "LOF" not in element_found: element_found["LIST OF FIGURES"] = pg_str

for i in range(chap1_index, len(doc)):
    text = doc[i].get_text().replace('\n', ' ')
    pg_str = full_page_map[i]
    
    for key, search_str in chapter_searches.items():
        if search_str in text and key not in element_found:
            element_found[key] = pg_str
    
    for t_m in re.finditer(r'Table\s+(\d+\.\d+)', text):
        t_id = t_m.group(1)
        key = f"Table_{t_id}"
        if key not in element_found: element_found[key] = pg_str
        
    for f_m in re.finditer(r'Fig(?:ure)?\s+(\d+\.\d+)', text):
        f_id = f_m.group(1)
        key = f"Fig_{f_id}"
        if key not in element_found: element_found[key] = pg_str

# Write to HTML
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

for ch in chapter_searches.keys():
    if ch in element_found:
        pg = element_found[ch]
        # TOC Replacement Regex: Looking for Exact Rows
        pattern = r'(<td[^>]*>\s*' + re.escape(ch) + r'\s*</td>\s*<td[^>]*>.*?</td>\s*<td[^>]*>)\s*(?:XX|[A-Za-z0-9]+)\s*(</td>)'
        html = re.sub(pattern, r'\g<1>' + str(pg) + r'\2', html, flags=re.DOTALL)

for lbl in ["TABLE OF CONTENTS", "LIST OF TABLES", "LIST OF FIGURES"]:
    if lbl in element_found:
        pg = element_found[lbl]
        pattern = r'(<td[^>]*>)\s*(' + re.escape(lbl) + r')\s*(</td>\s*<td[^>]*>)\s*(?:XX|[A-Za-z0-9]+)\s*(</td>)'
        html = re.sub(pattern, r'\g<1>\g<2>\g<3>' + str(pg) + r'\g<4>', html, flags=re.DOTALL)

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
    
subprocess.run([
    "google-chrome", "--headless", "--no-sandbox", "--no-pdf-header-footer",
    "--print-to-pdf=" + pdf_path,
    "file://" + html_path
], check=True)

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
print("Finished comprehensive layout scan and stamp")
