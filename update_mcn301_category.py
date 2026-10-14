
import csv
import shutil
from pathlib import Path

catalogue_path = Path("data/course_catalogue_2019.csv")
backup_path = Path("data/course_catalogue_2019_before_mcn301_category.csv")

# Create a backup before modifying anything.
shutil.copy2(catalogue_path, backup_path)

with catalogue_path.open("r", newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    courses = list(reader)

updated = False

for course in courses:
    if course["course_code"].strip() == "MCN 301":
        course["category"] = "Non-Credit"
        course["verification_status"] = (
            "Category verified from syllabus page 849; "
            "semester assigned from PDF page order and heading evidence"
        )
        updated = True
        print(
            f"Updated: {course['course_code']} - "
            f"{course['course_title']} | "
            f"Category: {course['category']}"
        )
        break

if not updated:
    print("ERROR: MCN 301 was not found. Catalogue not changed.")
else:
    with catalogue_path.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(courses)

    print(f"Backup saved to: {backup_path}")
    print("Update completed. ChromaDB was not modified.")
