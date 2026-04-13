import fitz
import re

doc = fitz.open("/home/dhakshin-raghav/final_report.pdf")
xx_pages = []

for i in range(len(doc)):
    text = doc[i].get_text()
    if re.search(r'\bXX\b', text, re.IGNORECASE):
        xx_pages.append(i)

print(f"Pages with 'XX': {xx_pages}")
for i in xx_pages:
    print(f"\n--- PAGE {i} ---")
    blocks = doc[i].get_text("dict")["blocks"]
    for b in blocks:
        if "lines" not in b: continue
        for l in b["lines"]:
            s = "".join([span["text"] for span in l["spans"]])
            if "xx" in s.lower():
                print(s)
