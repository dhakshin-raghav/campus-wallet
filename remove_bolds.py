import re

with open('project_report.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove <b> and </b>
html = re.sub(r'</?b>', '', html)
# Remove <strong> and </strong>
html = re.sub(r'</?strong>', '', html)

# Remove class="bold" or class="center bold" from <p> where it isn't the cover page's main title
# Or wait, let's keep it simple: the user wants to remove bold from everywhere except "headings and topics".
# So if a <p> has class="bold", we remove "bold" from it, except if its text is "PROJECT REPORT" or "CAMPUS CAFETERIA..."
# Actually, the cover page strings are:
# CAMPUS CAFETERIA PRE-BOOKING SYSTEM
# PROJECT REPORT
# DHAKSHIN RAGHAV A J
# BACHELOR OF TECHNOLOGY
# INFORMATION TECHNOLOGY
# BANNARI AMMAN INSTITUTE OF TECHNOLOGY
# ANNA UNIVERSITY: CHENNAI 600 025
# APRIL 2026

# It's much safer to just target the specific inline <p class="bold"> outside the cover page. 
# Let's split content into cover page and rest of the document.
cover_end = html.find("<!-- ══════════════════════════════════════════════ BONAFIDE CERTIFICATE ═══ -->")
if cover_end == -1: cover_end = 0

cover_page = html[:cover_end]
rest_of_doc = html[cover_end:]

# Strip 'bold' from class attributes in the rest of the document
rest_of_doc = re.sub(r'(class="[^"]*?)\bbold\b([^"]*?")', r'\1\2', rest_of_doc)
# Clean up empty spaces in class
rest_of_doc = rest_of_doc.replace('class=" "', 'class=""').replace('class=""', '')

# Remove strong and b from the entire document (to be safe!)
cover_page = re.sub(r'</?(strong|b)>', '', cover_page)
rest_of_doc = re.sub(r'</?(strong|b)>', '', rest_of_doc)

html = cover_page + rest_of_doc

with open('project_report.html', 'w', encoding='utf-8') as f:
    f.write(html)
