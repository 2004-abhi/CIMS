
import csv
from pathlib import Path

output = Path("data/first_year_course_evidence.csv")

courses = [
    ["MAT 101", "LINEAR ALGEBRA AND CALCULUS", "I", "BSC", "2"],
    ["PHT 100", "ENGINEERING PHYSICS A (FOR CIRCUIT BRANCHES)", "I", "BSC", "10,112"],
    ["CYT 100", "ENGINEERING CHEMISTRY", "I", "BSC", "30,132"],
    ["EST 100", "ENGINEERING MECHANICS", "I", "ESC", "39,141"],
    ["EST 110", "ENGINEERING GRAPHICS", "I", "ESC", "52,154"],
    ["EST 120", "BASICS OF CIVIL & MECHANICAL ENGINEERING", "I", "ESC", "61,163"],
    ["EST 130", "BASICS OF ELECTRICAL AND ELECTRONICS ENGINEERING", "I", "ESC", "73,175"],
    ["HUN 101", "LIFE SKILLS", "I", "MNC", "84"],
    ["PHL 120", "ENGINEERING PHYSICS LAB", "I", "BSC", "90,200"],
    ["CYL 120", "ENGINEERING CHEMISTRY LAB", "I", "BSC", "92,202"],
    ["ESL 120", "CIVIL & MECHANICAL WORKSHOP", "I", "", "94,204"],
    ["ESL 130", "ELECTRICAL & ELECTRONICS WORKSHOP", "I", "ESC", "99,209"],
    ["MAT 102", "VECTOR CALCULUS, DIFFERENTIAL EQUATIONS AND TRANSFORMS", "II", "BSC", "103"],
    ["PHT 110", "ENGINEERING PHYSICS B (FOR NON-CIRCUIT BRANCHES)", "II", "BSC", "122"],
    ["HUN 102", "PROFESSIONAL COMMUNICATION", "II", "MNC", "186"],
    ["EST 102", "PROGRAMMING IN C", "II", "ESC", "191"],
]

fields = [
    "course_code", "course_title", "semester", "category", "source_pages"
]

output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    writer.writerows(courses)

print(f"Created {output} with {len(courses)} evidence records.")
print("ESL 120 category remains blank pending confirmation.")
print("Main catalogue and ChromaDB were not modified.")
