import fitz

doc = fitz.open("/home/dhakshin-raghav/Downloads/final_report (1).pdf")

print("Checking for TOC pages...")
toc_pages = []
for i in range(len(doc)):
    text = doc[i].get_text()
    if "TABLE OF CONTENTS" in text.upper():
        toc_pages.append(i)

print(f"TOC Pages: {toc_pages}")
if toc_pages:
    for tp in toc_pages[:1]: # just first one
        print(f"--- PAGE {tp} ---")
        blocks = doc[tp].get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b: continue
            for l in b["lines"]:
                spans = l["spans"]
                text = "".join([s["text"] for s in spans]).strip()
                if text:
                    print(f"y0: {l['bbox'][1]:.1f} | x0: {l['bbox'][0]:.1f} | {text}")
