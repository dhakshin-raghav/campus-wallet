import fitz
import re
import subprocess
import os

pdf_path = "/home/dhakshin-raghav/projects/pre-booking-system/cafeteria_project_report.pdf"
html_path = "/home/dhakshin-raghav/projects/pre-booking-system/project_report.html"

# 1. Parse current PDF to find chapter start pages
doc = fitz.open(pdf_path)

toc_end_index = -1
for i in range(len(doc)):
    text = doc[i].get_text()
    if "TABLE OF CONTENTS" in text:
        toc_end_index = i

print(f"TOC ends at physical page index {toc_end_index}")

# Mapping from text header to physical page
chapter_pages = {}

for i in range(toc_end_index + 1, len(doc)):
    text = doc[i].get_text()
    arabic_pg = i - toc_end_index
    
    # Identify Chapters
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
    # Can expand this for Chapter 3 and beyond if needed, but the user HTML TOC
    # only lists up to 2.4 typically, let me check HTML TOC to be thorough

print(f"Chapter accurate pages: {chapter_pages}")

# 2. Update HTML TOC with accurate pages
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

for ch, pg in chapter_pages.items():
    # Looking for: <td ...>1.2</td> \n <td ...>Title</td> \n <td ...>OLD_PG</td>
    pattern = r'(<td[^>]*>\s*' + re.escape(ch) + r'\s*</td>\s*<td[^>]*>.*?</td>\s*<td[^>]*>)\s*\d+\s*(</td>)'
    html = re.sub(pattern, r'\g<1>' + str(pg) + r'\2', html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated HTML TOC")

# 3. Re-render PDF with Chrome (incorporating updated TOC)
subprocess.run([
    "google-chrome", "--headless", "--no-sandbox", "--no-pdf-header-footer",
    "--print-to-pdf=" + pdf_path,
    "file://" + html_path
], check=True)
print("Re-rendered PDF")

# 4. Open new PDF and stamp page numbers
doc = fitz.open(pdf_path)

roman_map = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']

for i in range(len(doc)):
    page = doc[i]
    rect = page.rect
    
    if i <= 1:
        continue
    elif i <= toc_end_index:
        text = roman_map[i]
    else:
        text = str(i - toc_end_index)
    
    text_rect = fitz.Rect(0, rect.height - 60, rect.width, rect.height - 30)
    page.insert_textbox(text_rect, text, fontsize=12, fontname="times-roman", align=1)

# Overwrite in place
doc.save("/home/dhakshin-raghav/projects/pre-booking-system/cafeteria_project_report_final.pdf")
os.rename("/home/dhakshin-raghav/projects/pre-booking-system/cafeteria_project_report_final.pdf", pdf_path)
print("Saved final PDF")
