from bs4 import BeautifulSoup
import re

with open("/home/dhakshin-raghav/projects/pre-booking-system/project_report.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

found_chapters = {}
for td in soup.find_all("td"):
    text = td.get_text(strip=True)
    if re.match(r'^\d+(\.\d+)?(\.\d+)?$', text):
        # Found a chapter number
        title_td = td.find_next_sibling("td")
        if title_td:
            title = title_td.get_text(strip=True)
            # Remove line breaks easily
            title = " ".join(title.split())
            if len(title) > 0 and title != "3.1": # Avoid accidental matching
                found_chapters[text] = title

print("toc_list = [")
for k, v in found_chapters.items():
    if v == "INTRODUCTION": v = "CHAPTER 1"
    if v == "LITERATURE SURVEY": v = "LITERATURE SURVEY"
    if v == "SYSTEM DIAGRAMS AND DESIGN": v = "SYSTEM DIAGRAMS AND DESIGN"
    if v == "SYSTEM TESTING AND VALIDATION": v = "SYSTEM TESTING AND VALIDATION"
    print(f'    ("{k}", "{v}"),')
print("]")
