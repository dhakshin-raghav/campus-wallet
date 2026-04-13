import re
with open("/home/dhakshin-raghav/projects/pre-booking-system/project_report.html", 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "<table" in line or "<img" in line or "Fig " in line or "Table " in line:
        print(f"L{i}: {line.strip()}")
