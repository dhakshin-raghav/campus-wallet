import fitz
import re
import subprocess
import os

pdf_path = "/home/dhakshin-raghav/Downloads/final_report.pdf"
html_path = "/home/dhakshin-raghav/projects/pre-booking-system/project_report.html"

# 1. Re-render to get exact text flow
subprocess.run([
    "google-chrome", "--headless", "--no-sandbox", "--no-pdf-header-footer",
    "--print-to-pdf=" + pdf_path,
    "file://" + html_path
], check=True)

# 2. Extract boundaries
doc = fitz.open(pdf_path)

abstract_index = -1
for i in range(len(doc)):
    text = doc[i].get_text()
    if re.search(r'\bABSTRACT\b', text, re.IGNORECASE) and not "TABLE OF CONTENTS" in text.upper():
        # Verifying it's actually the Abstract page
        if len(text.split()) > 20: 
            abstract_index = i
            break

if abstract_index == -1:
    print("Could not find ABSTRACT page.")
    abstract_index = 4 # Default to index 4 if missing

roman_map = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv']
roman_pg_map = {}
for i in range(1, abstract_index):
    roman_pg_map[i] = roman_map[i-1]

arabic_pg_map = {}
for i in range(abstract_index, len(doc)):
    arabic_pg_map[i] = str(i - abstract_index + 1)

full_page_map = {**roman_pg_map, **arabic_pg_map}
element_found = {}

chapter_searches = {
    "1": "CHAPTER 1", "1.1": "Background and Motivation", "1.2": "Role of Technology in Campus", 
    "1.3": "Problem Statement", "1.4": "Scope of the Project", "1.5": "Organization of the Report",
    "2": "LITERATURE SURVEY", "2.1": "Existing Systems and Approaches", "2.2": "Digital Ordering and Food-Tech",
    "2.3": "Campus Payment Systems", "2.4": "Real-Time Communication Patterns",
    "3": "OBJECTIVES AND METHODOLOGY", "3.1": "General Objectives", "3.2": "System Architecture",
    "3.3": "Module Description", "3.4": "Tools and Technologies Used", 
    "4": "RESULTS AND EVALUATION", "4.1": "System Implementation Results", "4.2": "Performance Analysis",
    "4.3": "Discussion of Results", 
    "5": "CONTINUOUS INTEGRATION", "5.1": "Overview of CI/CD Methodology", "5.2": "GitHub Actions Architecture",
    "5.3": "Jenkins Pipeline as Code", "5.4": "Docker Containerization Strategy", "5.5": "AWS EC2 Deployment Architecture",
    "5.6": "Deployment Script Architecture", "5.7": "Monitoring and Observability",
    "6": "CONCLUSION AND FUTURE", "6.1": "Conclusion", "6.2": "Future Works"
}

# Scan to find elements
for i in range(len(doc)):
    text = doc[i].get_text().replace('\n', ' ')
    pg_str = full_page_map.get(i, "XX")
    
    if "TABLE OF CONTENTS" in text and "TOC" not in element_found: element_found["TABLE OF CONTENTS"] = pg_str
    if "LIST OF TABLES" in text and "LOT" not in element_found: element_found["LIST OF TABLES"] = pg_str
    if "LIST OF FIGURES" in text and "LOF" not in element_found: element_found["LIST OF FIGURES"] = pg_str
    if "ABSTRACT" in text and "ABS" not in element_found and len(text.split())>20: element_found["ABSTRACT"] = pg_str
    if "ACKNOWLEDGEMENT" in text and "ACK" not in element_found: element_found["ACKNOWLEDGEMENT"] = pg_str

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

# Overwrite in HTML text buffer
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

for ch in chapter_searches.keys():
    if ch in element_found:
        pg = element_found[ch]
        pattern = r'(<td[^>]*>\s*' + re.escape(ch) + r'\s*</td>\s*<td[^>]*>.*?</td>\s*<td[^>]*>)\s*(?:XX|[A-Za-z0-9]+)\s*(</td>)'
        html = re.sub(pattern, r'\g<1>' + str(pg) + r'\2', html, flags=re.DOTALL)

for lbl in ["TABLE OF CONTENTS", "LIST OF TABLES", "LIST OF FIGURES", "ABSTRACT", "ACKNOWLEDGEMENT"]:
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
    
# Re-run after HTML is injected
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

tmp_path = "/home/dhakshin-raghav/Downloads/final_report_tmp.pdf"
doc.save(tmp_path)
os.rename(tmp_path, pdf_path)
print("Finished rendering finalized pdf globally with abstract at page 1.")
