import fitz

doc = fitz.open("/home/dhakshin-raghav/Downloads/Sample_table_of_contents.pdf")
print("=== REFERENCE TOC ===")
for page in doc:
    print(page.get_text())
    
    # Also get the exact x-coordinates to see "alignment"
    blocks = page.get_text("dict")["blocks"]
    print("--- Detailed BBox ---")
    for block in blocks:
        if "lines" not in block: continue
        for line in block["lines"]:
            spans = line["spans"]
            text = "".join([s["text"] for s in spans]).strip()
            if text:
                print(f"x0: {line['bbox'][0]:.1f} | {text}")
