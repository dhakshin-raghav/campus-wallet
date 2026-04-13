import fitz
import re
import subprocess
import os

pdf_path = "/home/dhakshin-raghav/projects/pre-booking-system/cafeteria_project_report.pdf"
html_path = "/home/dhakshin-raghav/projects/pre-booking-system/project_report.html"

# Run HTML format reset to allow valid replacements (just in case)
subprocess.run([
    "google-chrome", "--headless", "--no-sandbox", "--no-pdf-header-footer",
    "--print-to-pdf=" + pdf_path,
    "file://" + html_path
], check=True)

doc = fitz.open(pdf_path)

chap1_index = -1
for i in range(len(doc)):
    text = doc[i].get_text()
    if "CHAPTER 1" in text and "INTRODUCTION" in text:
        chap1_index = i
        break

print(f"CHAPTER 1 starts at physical page index {chap1_index}")

chapter_pages = {}
frontmatter_pages = {}

# Map Frontmatter
for i in range(2, chap1_index):
    text = doc[i].get_text().upper()
    roman_pg = ['i','ii','iii','iv','v','vi','vii','viii','ix','x','xi'][i]
    if "TABLE OF CONTENTS" in text and "TOC" not in frontmatter_pages: frontmatter_pages["TABLE OF CONTENTS"] = roman_pg
    if "LIST OF TABLES" in text and "LOT" not in frontmatter_pages: frontmatter_pages["LIST OF TABLES"] = roman_pg
    if "LIST OF FIGURES" in text and "LOF" not in frontmatter_pages: frontmatter_pages["LIST OF FIGURES"] = roman_pg

# Map Chapters
for i in range(chap1_index, len(doc)):
    text = doc[i].get_text()
    arabic_pg = i - chap1_index + 1
    
    if "CHAPTER 1" in text and "INTRODUCTION" in text:
        if "1" not in chapter_pages: chapter_pages["1"] = arabic_pg
    if "Background and Motivation" in text:
        if "1.1" not in chapter_pages: chapter_pages["1.1"] = arabic_pg
    if "Role of Technology in Campus Safeteria" in text or "Role of Technology in Campus" in text:
        if "1.2" not in chapter_pages: chapter_pages["1.2"] = arabic_pg
    if "Problem Statement" in text:
        if "1.3" not in chapter_pages: chapter_pages["1.3"] = arabic_pg
    if "Scope of the Project" in text:
        if "1.4" not in chapter_pages: chapter_pages["1.4"] = arabic_pg
    if "Organization of the Report" in text:
        if "1.5" not in chapter_pages: chapter_pages["1.5"] = arabic_pg
    if "CHAPTER 2" in text and "LITERATURE SURVEY" in text:
        if "2" not in chapter_pages: chapter_pages["2"] = arabic_pg
    if "Existing Systems and Approaches" in text:
        if "2.1" not in chapter_pages: chapter_pages["2.1"] = arabic_pg
    if "Digital Ordering and Food-Tech" in text:
        if "2.2" not in chapter_pages: chapter_pages["2.2"] = arabic_pg
    if "Campus Payment Systems" in text:
        if "2.3" not in chapter_pages: chapter_pages["2.3"] = arabic_pg
    if "Real-Time Communication Patterns" in text:
        if "2.4" not in chapter_pages: chapter_pages["2.4"] = arabic_pg

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Update Chapters explicitly
for ch, pg in chapter_pages.items():
    pattern = r'(<td[^>]*>\s*' + re.escape(ch) + r'\s*</td>\s*<td[^>]*>.*?</td>\s*<td[^>]*>)\s*[A-Za-z0-9]+\s*(</td>)'
    html = re.sub(pattern, r'\g<1>' + str(pg) + r'\2', html, flags=re.DOTALL)

# Update Frontmatter tables
for label, pg in frontmatter_pages.items():
    pattern = r'(<td[^>]*>)\s*(' + re.escape(label) + r')\s*(</td>\s*<td[^>]*>)\s*[A-Za-z0-9]+\s*(</td>)'
    html = re.sub(pattern, r'\g<1>\g<2>\g<3>' + str(pg) + r'\g<4>', html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

subprocess.run([
    "google-chrome", "--headless", "--no-sandbox", "--no-pdf-header-footer",
    "--print-to-pdf=" + pdf_path,
    "file://" + html_path
], check=True)

# 4. Stamp
doc = fitz.open(pdf_path)
roman_map = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii']

for i in range(len(doc)):
    page = doc[i]
    rect = page.rect
    if i <= 1:
        continue
    elif i < chap1_index:
        text = roman_map[i]
    else:
        text = str(i - chap1_index + 1)
    
    text_rect = fitz.Rect(0, rect.height - 50, rect.width, rect.height - 20)
    page.insert_textbox(text_rect, text, fontsize=12, fontname="times-roman", align=1)

tmp_path = "/home/dhakshin-raghav/projects/pre-booking-system/cafeteria_project_report_tmp.pdf"
doc.save(tmp_path)
os.rename(tmp_path, pdf_path)
print("SUCCESSFULLY APPLIED BOTH")
