import fitz
import re

pdf_path = "/home/dhakshin-raghav/final_report.pdf"
doc = fitz.open(pdf_path)

intro_idx = 9

# Map Chapters 5.3 and 5.4 exactly
ch_map = {}
for i in range(intro_idx, len(doc)):
    text = doc[i].get_text()
    if "5.3" in text and "JENKINS" in text.upper():
        if "5.3" not in ch_map:
            ch_map["5.3"] = str(i - intro_idx + 1)
    if "5.4" in text and "DOCKER" in text.upper():
        if "5.4" not in ch_map:
            ch_map["5.4"] = str(i - intro_idx + 1)

print(f"Mapped chapters: {ch_map}")

# 1. Apply Roman Numbers
roman_map = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']
for i in range(1, intro_idx):
    page = doc[i]
    roman_str = roman_map[i-1]
    
    rect = page.rect
    text_rect = fitz.Rect(0, rect.height - 40, rect.width, rect.height - 20)
    
    # We clear the bottom margin to avoid overlapping
    clear_rect = fitz.Rect(0, rect.height - 60, rect.width, rect.height)
    page.add_redact_annot(clear_rect, fill=(1, 1, 1))
    page.apply_redactions()
    
    page.insert_textbox(text_rect, roman_str, fontsize=12, fontname="times-roman", align=1)
    print(f"Stamping {roman_str} on page index {i}")

# 2. Fix the "XX" in the TOC. They are on page index 7 according to previous discovery.
for toc_idx in [7]: # Let's just scan all from 5 to 7 to be secure
    page = doc[toc_idx]
    blocks = page.get_text("dict")["blocks"]
    
    for block in blocks:
        if "lines" not in block: continue
        for line in block["lines"]:
            spans = line["spans"]
            text = "".join([s["text"] for s in spans]).strip()
            
            if "XX" in text.upper():
                # Which chapter does this line correspond to?
                # Sometimes the 5.3 is on the same line, or a few lines above.
                # If we just see an XX alone on the right side, we check its Y level.
                y0, y1 = line["bbox"][1], line["bbox"][3]
                
                # Check what text is on the same Y level on the page
                row_text = ""
                for b2 in blocks:
                    if "lines" not in b2: continue
                    for l2 in b2["lines"]:
                        y0_2, y1_2 = l2["bbox"][1], l2["bbox"][3]
                        if abs(y0 - y0_2) < 5:
                            row_text += "".join([s["text"] for s in l2["spans"]])
                
                num = ""
                if "5.3" in row_text:
                    num = ch_map.get("5.3", "")
                elif "5.4" in row_text:
                    num = ch_map.get("5.4", "")
                
                if num:
                    right_rect = fitz.Rect(430, y0-2, page.rect.width, y1+2)
                    page.add_redact_annot(right_rect, fill=(1,1,1))
                    page.apply_redactions()
                    
                    page.insert_text((page.rect.width - 70, y1 - 2), num, fontsize=12, fontname="times-roman")
                    print(f"Replaced XX with {num} on page {toc_idx}")

doc.save("/home/dhakshin-raghav/final_report_fixed.pdf")
print("Done!")
