
import csv
import json
import re
from pathlib import Path

DATA = Path("data")
OUTPUT = DATA / "v3_verified_page_preview.csv"


def normalize_code(value):
    return re.sub(r"\s+", "", value.upper())


def main():
    with (DATA / "course_catalogue_2019.csv").open(
        encoding="utf-8-sig", newline=""
    ) as file:
        catalogue = list(csv.DictReader(file))

    with (DATA / "semester_page_index.csv").open(
        encoding="utf-8-sig", newline=""
    ) as file:
        page_index = {
            int(row["pdf_page"]): row
            for row in csv.DictReader(file)
        }

    with (DATA / "pdf_full_text.jsonl").open(
        encoding="utf-8"
    ) as file:
        pages = {
            int(record["pdf_page"]): record.get("text", "")
            for record in map(json.loads, file)
            if record.get("pdf_page") is not None
        }

    rows = []

    for course in catalogue:
        status = course["verification_status"].lower()

        if not status.startswith("verified from"):
            continue

        try:
            page = int(course["source_pages"])
        except (ValueError, TypeError):
            continue

        text = pages.get(page, "")
        index_row = page_index.get(page, {})

        code = course["course_code"].strip()
        normalized = normalize_code(code)

        indexed_codes = {
            normalize_code(item)
            for item in index_row.get("course_codes", "").split(";")
            if item.strip()
        }

        if normalized not in normalize_code(text) and normalized not in indexed_codes:
            continue

        rows.append({
            "course_code": code,
            "course_title": course["course_title"],
            "semester": course["semester"],
            "category": course["category"],
            "source_page": page,
            "verification_status": course["verification_status"],
            "page_type_candidate": index_row.get(
                "page_type_candidate", ""
            ),
        })

    with OUTPUT.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "course_code",
                "course_title",
                "semester",
                "category",
                "source_page",
                "verification_status",
                "page_type_candidate",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} verified page matches to {OUTPUT}")
    print("No ChromaDB records were changed.")


if __name__ == "__main__":
    main()
