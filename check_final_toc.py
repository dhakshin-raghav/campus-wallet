import fitz

doc = fitz.open("/home/dhakshin-raghav/final_report.pdf")
toc_pages = []
for i in range(len(doc)):
    if "TABLE OF CONTENTS" in doc[i].get_text().upper():
        toc_pages.append(i)

print(f"TOC Pages: {toc_pages}")
if len(toc_pages) > 0:
    for i in toc_pages:
        print(f"--- PAGE {i} ---")
        print(doc[i].get_text())
