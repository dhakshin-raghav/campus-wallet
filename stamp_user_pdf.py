import fitz
import re
import os

pdf_path = "/home/dhakshin-raghav/Downloads/cafeteria_project_report (1).pdf"
out_path = "/home/dhakshin-raghav/Downloads/cafeteria_project_report_numbered.pdf"
doc = fitz.open(pdf_path)

toc_page_indices = []
intro_page_index = -1

for i in range(len(doc)):
    text = doc[i].get_text()
    if "TABLE OF CONTENTS" in text.upper():
        toc_page_indices.append(i)
    if "CHAPTER 1" in text.upper() and ("INTRODUCTION" in text.upper() or "BACKGROUND" in text.upper()):
        if intro_page_index == -1:
            intro_page_index = i

# If TOC spans multiple pages, they are sequential
if len(toc_page_indices) > 0 and toc_page_indices[0] + 1 != intro_page_index:
    # Add page 2 of TOC if there's a gap
    if toc_page_indices[0] + 1 not in toc_page_indices and "1." in doc[toc_page_indices[0] + 1].get_text():
        toc_page_indices.append(toc_page_indices[0] + 1)

print(f"TOC Pages: {toc_page_indices}")
print(f"Intro Page: {intro_page_index}")

# Stamping page numbers at bottom center starting from Introduction
for i in range(intro_page_index, len(doc)):
    page = doc[i]
    arabic_num = str(i - intro_page_index + 1)
    
    rect = page.rect
    # Coordinates for bottom center. A4 is roughly 595x842. Bottom center is around y=800.
    text_rect = fitz.Rect(0, rect.height - 40, rect.width, rect.height - 20)
    
    # Check if there is already a page number at bottom
    # We can try to redact the bottom area first to clear old page numbers
    # We'll just redact the bottom 50 points
    clear_rect = fitz.Rect(0, rect.height - 60, rect.width, rect.height)
    page.add_redact_annot(clear_rect, fill=(1, 1, 1))
    page.apply_redactions()
    
    page.insert_textbox(text_rect, arabic_num, fontsize=12, fontname="times-roman", align=1)

# Now, we need to locate chapters on the pages and map them
# To keep it simple, we'll just search for exact "1.1 Content", etc.
headers_to_find = [
    "1.1", "1.2", "1.3", "1.4", "1.5",
    "2.1", "2.2", "2.3", "2.4",
    "3.1", "3.2", "3.3", "3.4", "3.5",
    "4.1", "4.2", "4.3", "4.4", "4.5",
    "5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8",
    "6.1", "6.2",
    "CHAPTER 1", "CHAPTER 2", "CHAPTER 3", "CHAPTER 4", "CHAPTER 5", "CHAPTER 6"
]

header_map = {}
for i in range(intro_page_index, len(doc)):
    text = doc[i].get_text()
    arabic_num = str(i - intro_page_index + 1)
    
    for h in headers_to_find:
        # Avoid matching "1.1" when the text has "1.10" or something. So we use regex boundary.
        # However, getting just the number is enough. "CHAPTER 1" is safe.
        if h not in header_map:
            # simple check if h is in text alone on a line or something
            # Let's search for the exact block or just use regex
            if re.search(r'\b' + re.escape(h) + r'\b', text):
                header_map[h] = arabic_num

# Now we need to overwrite the numbers in the TOC.
# In the TOC, the chapter headers are on the left or middle, and numbers are on the right margin.
# We will iterate through all lines in TOC pages and find the numbers at x > 400.
for t_idx in toc_page_indices:
    page = doc[t_idx]
    
    # Strategy: find occurrences of the headers in the TOC.
    # Then look at the right side of those headers and redact the number, replace with the newly found number.
    blocks = page.get_text("dict")["blocks"]
    
    for block in blocks:
        if "lines" not in block: continue
        for line in block["lines"]:
            spans = line["spans"]
            text = "".join([s["text"] for s in spans]).strip()
            
            # See if the text starts with or exactly matches one of our headers
            # Often TOC lines look like "1.1 Background and Motivation       ......       4"
            # Or the number is in a separate span!
            for h in headers_to_find:
                if re.search(r'\b' + re.escape(h) + r'\b', text) or h in text:
                    if h in header_map:
                        arabic_num = header_map[h]
                        # Redact numbers on the right side of this y-coordinate
                        y0, y1 = line["bbox"][1], line["bbox"][3]
                        # Rect on the right side (x > 450)
                        right_rect = fitz.Rect(430, y0-2, page.rect.width, y1+2)
                        page.add_redact_annot(right_rect, fill=(1,1,1))
                        page.apply_redactions()
                        
                        # Insert new text
                        page.insert_text((page.rect.width - 70, y1 - 2), arabic_num, fontsize=12, fontname="times-roman")
                    break

doc.save(out_path)
print(f"Saved to {out_path}")
