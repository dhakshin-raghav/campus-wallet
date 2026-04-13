import fitz
doc = fitz.open("/home/dhakshin-raghav/projects/pre-booking-system/cafeteria_project_report.pdf")
for i in range(12):
    print(f"----- PAGE {i} -----")
    print(doc[i].get_text()[:100].replace('\n', ' '))
