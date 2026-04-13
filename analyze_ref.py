import fitz

ref_path = "/home/dhakshin-raghav/Downloads/MINIPROJECT_REPORT (1).pdf"
doc = fitz.open(ref_path)

# Analyze pages 8-20 (content chapters) for font/indentation patterns
for pg_idx in [8, 9, 10, 11, 12, 15, 20, 25, 30]:
    if pg_idx >= len(doc):
        continue
    page = doc[pg_idx]
    print(f"\n{'='*80}")
    print(f"PAGE {pg_idx + 1}")
    print(f"{'='*80}")
    
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if not text:
                    continue
                font = span["font"]
                size = round(span["size"], 1)
                x0 = round(span["origin"][0], 1)
                is_bold = "Bold" in font or "bold" in font
                flags = span["flags"]
                
                # Only print representative samples
                if len(text) > 3:
                    bold_marker = "**BOLD**" if is_bold else ""
                    print(f"  x={x0:6.1f}  size={size:5.1f}  font={font:<35s}  {bold_marker:10s} | {text[:80]}")
