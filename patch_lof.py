import fitz
import re

src_path = "/home/dhakshin-raghav/projects/pre-booking-system/cafeteria_project_report.pdf"
dst_path = "/home/dhakshin-raghav/final_report.pdf"

src_doc = fitz.open(src_path)
dst_doc = fitz.open(dst_path)

# 1. Find LOF page in src_doc
lof_idx = -1
for i in range(len(src_doc)):
    text = src_doc[i].get_text()
    if "LIST OF FIGURES" in text:
        lof_idx = i
        break

if lof_idx == -1:
    print("Could not find LIST OF FIGURES page in source doc!")
    exit(1)

print(f"Found LOF at src index: {lof_idx}")

# Extract page 
src_doc.select([lof_idx])
lof_page = src_doc[0]

# 2. Map Figures in dst_doc
dst_intro_idx = 9

fig_map = {}
for i in range(dst_intro_idx, len(dst_doc)):
    text = dst_doc[i].get_text()
    arabic_num = str(i - dst_intro_idx + 1)
    
    for fm in re.finditer(r'Fig(?:ure)?\s+(\d+\.\d+)', text):
        fid = fm.group(1)
        if fid not in fig_map:
            fig_map[fid] = arabic_num

print(f"Figures mapped in dst_doc: {fig_map}")

# 3. Update numbers on the lof_page
blocks = lof_page.get_text("dict")["blocks"]

for block in blocks:
    if "lines" not in block: continue
    for line in block["lines"]:
        spans = line["spans"]
        text = "".join([s["text"] for s in spans]).strip()
        
        # Check if line matches a figure ID in the map
        for fid, num in fig_map.items():
            if fid in text or re.search(r'\b'+re.escape(fid)+r'\b', text):
                y0, y1 = line["bbox"][1], line["bbox"][3]
                
                # Check for numbers on the right side of this y-coordinate
                # We redact X > 450
                right_rect = fitz.Rect(430, y0-2, lof_page.rect.width, y1+2)
                lof_page.add_redact_annot(right_rect, fill=(1,1,1))
                lof_page.apply_redactions()
                
                # Insert the correct mapped number
                lof_page.insert_text((lof_page.rect.width - 70, y1 - 2), num, fontsize=12, fontname="times-roman")
                print(f"Updated Figure {fid} in LOF to page {num}")
                break

# 4. We must also redact the bottom of the lof_page to remove its previous Roman/Arabic stamping 
# and stamp the correct Roman numeral for dst_doc.
rect = lof_page.rect
clear_rect = fitz.Rect(0, rect.height - 60, rect.width, rect.height)
lof_page.add_redact_annot(clear_rect, fill=(1, 1, 1))
lof_page.apply_redactions()

roman_map = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']
# If intro was at 9, and LOF is inserted at 9, the LOF gets roman_map[8] which is 'ix'.
roman_str = roman_map[dst_intro_idx - 1]
text_rect = fitz.Rect(0, rect.height - 40, rect.width, rect.height - 20)
lof_page.insert_textbox(text_rect, roman_str, fontsize=12, fontname="times-roman", align=1)
print(f"Stamped LOF page with {roman_str}")

# 5. Insert lof_page into dst_doc at dst_intro_idx
dst_doc.insert_pdf(src_doc, from_page=0, to_page=0, start_at=dst_intro_idx)

# Save
dst_doc.save("/home/dhakshin-raghav/final_report_patched.pdf")
print("Saved to final_report_patched.pdf")
