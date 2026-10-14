
import csv
from pathlib import Path

catalogue = Path("data/course_catalogue_2019.csv")

with catalogue.open("r", newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    rows = list(reader)

for row in rows:
    if row["course_code"].strip() == "CST 362":
        row["semester"] = "VI"
        row["category"] = "PEC"
        row["verification_status"] = (
            "Code discrepancy: syllabus p747 says CST 362; "
            "index p491 says CSL 362"
        )
        break
else:
    raise ValueError("CST 362 was not found in the catalogue.")

with catalogue.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Recorded the code discrepancy.")
print("Semester VI and category PEC are supported by index page 491.")
print("The syllabus-page code CST 362 has been preserved.")
print("ChromaDB was not modified.")

