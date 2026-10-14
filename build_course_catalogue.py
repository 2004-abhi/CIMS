
import csv
from collections import defaultdict
from pathlib import Path

source = Path("data/course_heading_review_v3.csv")
output = Path("data/course_catalogue_2019.csv")

groups = defaultdict(list)

with source.open("r", encoding="utf-8-sig", newline="") as file:
    for row in csv.DictReader(file):
        code = row.get("course_code_candidate", "").strip().upper()
        title = row.get("title_candidate", "").strip()

        if code:
            groups[code].append({
                "title": title,
                "page": row.get("pdf_page", "").strip(),
                "review_note": row.get("review_note", "").strip(),
            })

fields = [
    "scheme",
    "course_code",
    "course_title",
    "source_pages",
    "semester",
    "category",
    "verification_status",
]

with output.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for code, records in sorted(groups.items()):
        titles = sorted({
            record["title"]
            for record in records
            if record["title"]
        })

        pages = sorted({
            record["page"]
            for record in records
            if record["page"]
        }, key=int)

        writer.writerow({
            "scheme": "2019",
            "course_code": code,
            "course_title": " | ".join(titles),
            "source_pages": ", ".join(pages),
            "semester": "",
            "category": "",
            "verification_status": "Candidate - needs verification",
        })

print(f"Catalogue created: {output}")
print(f"Unique course-code records: {len(groups)}")
print("Semester and category are intentionally left blank until verified.")
