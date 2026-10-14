
import csv
from collections import defaultdict
from pathlib import Path

source = Path("data/course_heading_review_v3.csv")
output = Path("data/course_duplicate_report.csv")

groups = defaultdict(list)

with source.open("r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        code = row.get("course_code_candidate", "").strip()
        if code:
            groups[code].append(row)

with output.open("w", encoding="utf-8", newline="") as file:
    fields = [
        "course_code",
        "title",
        "source_pages",
        "record_count",
        "status",
    ]

    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for code, rows in groups.items():
        if len(rows) > 1:
            titles = sorted({
                row.get("title_candidate", "").strip()
                for row in rows
            })

            writer.writerow({
                "course_code": code,
                "title": " | ".join(titles),
                "source_pages": ", ".join(
                    row.get("pdf_page", "").strip()
                    for row in rows
                ),
                "record_count": len(rows),
                "status": "Needs verification",
            })

print(f"Duplicate report saved to: {output}")
