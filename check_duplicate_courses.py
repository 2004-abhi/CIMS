
import csv
from collections import defaultdict

path = "data/course_catalogue_2019.csv"

with open(path, "r", newline="", encoding="utf-8-sig") as file:
    courses = list(csv.DictReader(file))

by_code = defaultdict(list)

for course in courses:
    code = course.get("course_code", "").strip().upper()
    if code:
        by_code[code].append(course)

duplicates = {
    code: records
    for code, records in by_code.items()
    if len(records) > 1
}

print(f"Total records: {len(courses)}")
print(f"Unique course codes: {len(by_code)}")
print(f"Duplicate course codes: {len(duplicates)}")

for code, records in duplicates.items():
    print(f"\n{code}:")
    for course in records:
        print(
            f"  {course['course_title']} | "
            f"Semester {course['semester']} | "
            f"Category {course['category']} | "
            f"Pages {course['source_pages']}"
        )

print("\nInspection only. No files were modified.")
