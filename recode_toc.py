import fitz
import re

pdf_path = "/home/dhakshin-raghav/Downloads/final_report (1).pdf"
dst_path = "/home/dhakshin-raghav/Downloads/final_report_patched.pdf"

doc = fitz.open(pdf_path)

# Locate structure
abstract_idx = -1
toc_indices = []

for i in range(len(doc)):
    text = doc[i].get_text()
    if re.search(r'\bABSTRACT\b', text, re.IGNORECASE) and "TABLE OF CONTENTS" not in text.upper():
        if len(text.split()) > 20:
            abstract_idx = i
    if "TABLE OF CONTENTS" in text.upper():
        toc_indices.append(i)

if abstract_idx == -1:
    print("FATAL: Could not locate ABSTRACT.")
    exit(1)

print(f"Abstract Index: {abstract_idx}")
print(f"TOC Indices: {toc_indices}")

# Assign Page Numbers mapping
arabic_pg_map = {}
for i in range(abstract_idx, len(doc)):
    arabic_pg_map[i] = str(i - abstract_idx + 1)

# Now apply the stamping natively to the bottom of the pages.
for i in range(abstract_idx, len(doc)):
    page = doc[i]
    arabic_num = arabic_pg_map[i]
    
    rect = page.rect
    # Clear the old Arabic numbers the user might have inserted from Word that are incorrect
    clear_rect = fitz.Rect(0, rect.height - 60, rect.width, rect.height)
    page.add_redact_annot(clear_rect, fill=(1, 1, 1))
    page.apply_redactions()
    
    text_rect = fitz.Rect(0, rect.height - 40, rect.width, rect.height - 20)
    page.insert_textbox(text_rect, arabic_num, fontsize=12, fontname="times-roman", align=1)

# Map Chapters for updating TOC
ch_map = {}
chapters_to_find = [
    "1", "1.1", "1.2", "1.3", "1.4", "1.5",
    "2", "2.1", "2.2", "2.3", "2.4",
    "3", "3.1", "3.2", "3.3", "3.4", "3.5",
    "4", "4.1", "4.2", "4.3", "4.4", "4.5",
    "5", "5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8",
    "6", "6.1", "6.2",
    "BONAFIDE CERTIFICATE", "DECLARATION", "ACKNOWLEDGEMENT", "ABSTRACT",
    "INTRODUCTION", "LITERATURE SURVEY", "OBJECTIVES AND METHODOLOGY",
    "RESULTS AND EVALUATION", "CONTINUOUS INTEGRATION", "CONCLUSION AND FUTURE",
    "REFERENCES", "TABLE OF CONTENTS", "LIST OF FIGURES", "LIST OF TABLES"
]

# A more robust exact line search
for i in range(len(doc)):
    pg_str = arabic_pg_map.get(i, "XX") # if it's before abstract, we don't map to arabic, but Roman? 
    # Actually wait. The user only said "the page numbering should start from 1 on abstract".
    # Previous indexes like Bonafide might get Roman from the Word doc already, or we can just leave it alone.
    
    text = doc[i].get_text()
    # We just do basic matching
    for ch in chapters_to_find:
        # Avoid matching "1" when it's "1.1", or "5" when it's "5.5"
        if re.search(r'^\s*'+re.escape(ch)+r'\b', text, re.MULTILINE):
            if ch not in ch_map:
                ch_map[ch] = pg_str
        elif ch in ["BONAFIDE CERTIFICATE", "DECLARATION", "ACKNOWLEDGEMENT", "ABSTRACT", "TABLE OF CONTENTS", "LIST OF FIGURES", "LIST OF TABLES"]:
            if ch in text.upper():
                if ch not in ch_map:
                    ch_map[ch] = pg_str

print("Dynamic Index Map:", ch_map)

# Redraw the TOC Alignment
# For each TOC page, we parse its "lines"
for t_idx in toc_indices:
    page = doc[t_idx]
    blocks = page.get_text("dict")["blocks"]
    
    # We will aggregate all texts by vertical Y thresholds
    rows = []
    headers_y = 0
    header_found = False
    
    for b in blocks:
        if "lines" not in b: continue
        for l in b["lines"]:
            y = l["bbox"][1]
            spans = l["spans"]
            text = "".join([s["text"] for s in spans]).strip()
            if not text: continue
            
            # Group into rows
            matched_row = False
            for r in rows:
                if abs(r['y'] - y) < 8:
                    r['texts'].append({'x': l["bbox"][0], 'text': text})
                    matched_row = True
                    break
            
            if not matched_row:
                rows.append({'y': y, 'texts': [{'x': l["bbox"][0], 'text': text}]})

            if "TABLE OF CONTENTS" in text.upper() or "LIST OF" in text.upper():
                header_found = True
            if "CHAPTER" in text.upper() or "TITLE" in text.upper():
                headers_y = y

    # Redact the body
    if headers_y > 0:
        redact_rect = fitz.Rect(30, headers_y + 20, page.rect.width - 30, page.rect.height - 70)
        page.add_redact_annot(redact_rect, fill=(1, 1, 1))
        page.apply_redactions()
        
        # Now we mathematically redraw them based on what was in the rows
        y_cursor = headers_y + 35
        
        # Sort rows top-to-bottom
        rows.sort(key=lambda x: x['y'])
        
        for r in rows:
            if r['y'] <= headers_y + 15: continue
            # skip the footer
            if r['y'] > page.rect.height - 80: continue
            
            # Sort texts left-to-right
            t_list = sorted(r['texts'], key=lambda x: x['x'])
            full_text = " ".join([t['text'] for t in t_list]).upper()
            
            # Parse pieces
            # Possible formats:
            # 1. "1.1 BACKGROUND AND MOTIVATION 11"
            # 2. "INTRODUCTION 8"
            
            chapter_no = ""
            title = ""
            
            # Search for chapter prepended string like "2", "3.1"
            m = re.match(r'^([\d\.]+)\s+(.*)', full_text)
            if m:
                chapter_no = m.group(1)
                title = m.group(2)
            else:
                title = full_text
            
            # Try to strip away the old page number at the end if it exists.
            # usually like "MOTIVATION 13"
            pm = re.search(r'\s+([A-Za-z0-9ivxlc]+)$', title)
            if pm:
                title = title[:pm.start()].strip()
            
            if not title: continue
            
            # Filter matches
            # Let's map real page
            real_pg = "XX"
            for k in ch_map.keys():
                if k == title:
                    real_pg = ch_map[k]
                    break
            
            if real_pg == "XX" and chapter_no in ch_map:
                real_pg = ch_map[chapter_no]
            
            # Now redraw them strictly aligned perfectly!
            font = "times-roman"
            fontSize = 12
            # X constraints based exactly on sample layout
            if chapter_no:
                page.insert_textbox(fitz.Rect(70, y_cursor, 130, y_cursor+15), chapter_no, fontsize=fontSize, fontname=font, align=0)
            
            page.insert_textbox(fitz.Rect(130, y_cursor, 450, y_cursor+15), title, fontsize=fontSize, fontname=font, align=0)
            
            if real_pg != "XX":
                page.insert_textbox(fitz.Rect(450, y_cursor, 490, y_cursor+15), str(real_pg), fontsize=fontSize, fontname=font, align=2)

            y_cursor += 20 # fixed line spacing

doc.save(dst_path)
print("Finished drawing geometric native TOC mapping.")
