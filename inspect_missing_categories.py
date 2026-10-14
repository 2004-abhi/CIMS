
import csv

file_path = "data/course_catalogue_2019.csv"

with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    courses = list(reader)

missing = [
    course for course in courses
    if not course.get("category", "").strip()
]

print(f"Courses missing category: {len(missing)}")
print("-" * 80)

for course in missing:
    print(
        f"Code: {course.get('course_code', '')} | "
        f"Title: {course.get('course_title', '')} | "
        f"Semester: {course.get('semester', '')} | "
        f"Pages: {course.get('source_pages', '')} | "
        f"Status: {course.get('verification_status', '')}"
    )

print("-" * 80)
print("Inspection only. No files were modified.")
