
import csv
from pathlib import Path

SOURCE = Path("data/course_heading_review_v2.csv")
OUTPUT = Path("data/course_heading_review_v3.csv")

with SOURCE.open(
    "r", encoding="utf-8-sig", newline=""
) as file:
    reader = csv.DictReader(file)
    rows = list(reader)
    fieldnames = list(reader.fieldnames or [])

# Add a review-notes column without modifying the original file.
if "review_note" not in fieldnames:
    fieldnames.append("review_note")

for row in rows:
    page = row["pdf_page"]
    code = row["course_code_candidate"]

    row["review_note"] = ""

    # Correct a false course-code match.
    if page == "307":
        row["course_code_candidate"] = "MAT 206"
        row["title_candidate"] = "GRAPH THEORY"
        row["review_note"] = (
            "Corrected using the course heading on PDF page 307."
        )

    # These pages contain the same HUT 200 course heading.
    elif page in {"462", "484"} and code == "HUT 200":
        row["title_candidate"] = "PROFESSIONAL ETHICS"
        row["review_note"] = (
            "Title recovered from page text; "
            "check whether this is a repeated syllabus record."
        )

with OUTPUT.open(
    "w", encoding="utf-8-sig", newline=""
) as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Created:", OUTPUT)
print("Candidate rows:", len(rows))
print("Original v2 file remains unchanged.")
