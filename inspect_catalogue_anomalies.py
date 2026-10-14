
import csv

path = "data/course_catalogue_2019.csv"

with open(path, "r", newline="", encoding="utf-8-sig") as file:
    courses = list(csv.DictReader(file))

print(f"Total records: {len(courses)}")

print("\n--- Records with blank verification status ---")
blank_status = [
    c for c in courses
    if not c.get("verification_status", "").strip()
]

if blank_status:
    for c in blank_status:
        print(
            f"{c['course_code']} | {c['course_title']} | "
            f"Semester {c['semester']} | Pages {c['source_pages']}"
        )
else:
    print("None")

print("\n--- Python course records ---")
for c in courses:
    if "362" in c.get("course_code", ""):
        print(
            f"Code: {c['course_code']} | "
            f"Title: {c['course_title']} | "
            f"Semester: {c['semester']} | "
            f"Category: {c['category']} | "
            f"Pages: {c['source_pages']} | "
            f"Status: {c['verification_status']}"
        )

print("\nInspection only. No files were modified.")
