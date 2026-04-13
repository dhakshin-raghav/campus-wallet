with open("/home/dhakshin-raghav/projects/pre-booking-system/project_report.html", "r") as f:
    lines = f.readlines()

print("--- TABLES ---")
for i, line in enumerate(lines):
    if "<table" in line and "border:none;" not in line:
        print(f"\n--- TABLE AT L{i} ---")
        for j in range(max(0, i-5), i+1):
            print(f"L{j}: {lines[j].strip()}")

print("\n--- IMAGES/DIAGRAMS ---")
for i, line in enumerate(lines):
    if "<img" in line or ("border: 2px solid" in line and "text-align: center" in line):
        print(f"\n--- DIAGRAM AT L{i} ---")
        for j in range(max(0, i-5), i+2):
            print(f"L{j}: {lines[j].strip()}")
