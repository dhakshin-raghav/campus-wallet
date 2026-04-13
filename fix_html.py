import re

with open('project_report.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace guide name
content = re.sub(r'(?i)Mr\.\s*SATHEESH\s*N\s*P', 'Prof. Kavitha V', content)
content = content.replace('Mr. Satheesh N P', 'Prof. Kavitha V')

ch4_marker = "<!-- ═══════════════════════════════════════════════ CHAPTER 4 ═══ -->"
ch5_marker = "<!-- ═══════════════════════════════════════════════ CHAPTER 5 ═══ -->"
sys_diagrams_marker = "<!-- ═══════════════════════════════════════════ SYSTEM TESTING ═══ -->"
testing_chapter_marker = "<!-- ═══════════════════════════════════════════ TESTING CHAPTER ═══ -->"
body_end_marker = "</body>"

idx_sys = content.find(sys_diagrams_marker)
idx_testing = content.find(testing_chapter_marker)
idx_body = content.find(body_end_marker)

if idx_sys != -1 and idx_testing != -1 and idx_body != -1:
    part_sys_diag = content[idx_sys:idx_testing]
    part_testing = content[idx_testing:idx_body]

    # Remove them from the bottom
    content = content[:idx_sys] + content[idx_body:]

    # re-find chapters because string length changed
    content = content.replace(ch4_marker, part_sys_diag + "\n  " + ch4_marker)
    content = content.replace(ch5_marker, part_testing + "\n  " + ch5_marker)

def remove_bold_from_p(match):
    text = match.group(0)
    # Only process if it's not the Cover Page elements which shouldn't be stripped
    # But wait, the cover page has <p class="center bold"...> which the user might have meant too?
    # "no bold other than tiltle so reove bold in para contents"
    # Actually, cover page should be bold for titles.
    # Let's just remove <strong> and <b> from all <p> 
    text = re.sub(r'</?(strong|b)>', '', text)
    # Remove 'bold' from class
    text = re.sub(r'(class="[^"]*?)\bbold\b([^"]*?")', r'\1\2', text)
    # Cleanup empty class=" "
    text = text.replace('class=" "', 'class=""')
    text = text.replace('class=""', '')
    return text

# We will apply remove_bold_from_p to ALL <p> tags
# Wait, cover page has <p class="center bold... DHAKSHIN RAGHAV...
# The user said "no bold other than tiltle so reove bold in para contents"
# That means the main report paragraphs, not the title page!
# Title page is inside <div class="cover-page">.
# Let's split content into cover page and rest of body.

cover_end = content.find("<!-- ═══════════════════════════════════════════════ CHAPTER 1 ═══ -->")
if cover_end == -1: cover_end = 0

cover_page = content[:cover_end]
rest_page = content[cover_end:]

rest_page = re.sub(r'(?s)<p\b[^>]*>.*?</p>', remove_bold_from_p, rest_page)
# We might also have <li> that contain <strong>
def remove_bold_from_li(match):
    text = match.group(0)
    text = re.sub(r'</?(strong|b)>', '', text)
    return text
rest_page = re.sub(r'(?s)<li\b[^>]*>.*?</li>', remove_bold_from_li, rest_page)

# What about bold in lists in chapter 4.5 tables or fig captions? 
# "remove bold in para contents". So just <p> and <li> is fine.
# Also there are <strong> in <p> in fig captions: e.g. <p><strong>Customer Flow:</strong> ...
rest_page = rest_page.replace('<strong>', '').replace('</strong>', '')

content = cover_page + rest_page

with open('project_report.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML fixed.")
