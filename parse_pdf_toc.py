import fitz

pdf_path = "/home/dhakshin-raghav/Downloads/cafeteria_project_report (1).pdf"
doc = fitz.open(pdf_path)

# Let's find TOC and Introduction pages
toc_page = -1
intro_page = -1

for i in range(len(doc)):
    text = doc[i].get_text()
    if "TABLE OF CONTENTS" in text.upper():
        toc_page = i
    if "CHAPTER 1" in text.upper() and ("INTRODUCTION" in text.upper() or "BACKGROUND" in text.upper()):
        if intro_page == -1:  # Usually Intro section starts after TOC
            intro_page = i

print(f"TOC Page (0-indexed): {toc_page}")
print(f"Intro Page (0-indexed): {intro_page}")

if toc_page != -1:
    print("----- TOC Text Sample -----")
    text = doc[toc_page].get_text("dict")
    for block in text.get("blocks", []):
        if "lines" not in block: continue
        for line in block["lines"]:
            s = "".join([span["text"] for span in line["spans"]])
            if len(s.strip()) > 3:
                print(s)
    
    # Check if TOC spans multiple pages
    if toc_page + 1 != intro_page and toc_page + 1 < len(doc):
        text2 = doc[toc_page + 1].get_text()
        if "CHAPTER" in text2 or "1." in text2:
            print("----- TOC Page 2 Text Sample -----")
            text_dict = doc[toc_page + 1].get_text("dict")
            for block in text_dict.get("blocks", []):
                if "lines" not in block: continue
                # just print a few lines
                s = "".join([span["text"] for span in block["lines"][0]["spans"]])
                print(s)
