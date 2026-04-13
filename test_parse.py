import fitz
doc = fitz.open("/home/dhakshin-raghav/projects/pre-booking-system/cafeteria_project_report.pdf")
for i in range(len(doc)):
    text = doc[i].get_text()
    if "TABLE OF CONTENTS" in text:
        print(f"TOC found at page {i}")
        break
