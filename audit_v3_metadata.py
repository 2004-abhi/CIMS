
import csv
import json
from pathlib import Path
from collections import Counter

DATA_DIR = Path("data")

TEXT_FILE = DATA_DIR / "pdf_full_text.jsonl"
INDEX_FILE = DATA_DIR / "semester_page_index.csv"
CATALOGUE_FILE = DATA_DIR / "course_catalogue_2019.csv"
OUTPUT_FILE = DATA_DIR / "v3_metadata_audit.csv"


def load_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main():
    for path in (TEXT_FILE, INDEX_FILE, CATALOGUE_FILE):
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    # Load page index and catalogue.
    index_rows = load_csv(INDEX_FILE)
    catalogue_rows = load_csv(CATALOGUE_FILE)

    index_by_page = {
        int(row["pdf_page"]): row
        for row in index_rows
    }

    # Count extracted pages and validate JSONL page numbers.
    extracted_pages = set()

    with TEXT_FILE.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            record = json.loads(line)
            page = int(record["pdf_page"])
            extracted_pages.add(page)

    # Only catalogue entries with an integer source page can be checked.
    report = []

    for course in catalogue_rows:
        code = course["course_code"].strip().upper()
        source_pages = course["source_pages"].strip()

        try:
            page = int(source_pages)
        except (TypeError, ValueError):
            page = None

        index_row = index_by_page.get(page, {}) if page else {}
        page_exists = page in extracted_pages if page else False

        indexed_codes = {
            item.strip().upper()
            for item in index_row.get("course_codes", "").split(";")
            if item.strip()
        }

        report.append({
            "course_code": code,
            "course_title": course["course_title"],
            "catalogue_semester": course["semester"],
            "category": course["category"],
            "source_page": source_pages,
            "verification_status": course["verification_status"],
            "source_page_exists": page_exists,
            "index_detected_course_code": code in indexed_codes,
            "index_course_codes": "; ".join(sorted(indexed_codes)),
            "page_type_candidate": index_row.get(
                "page_type_candidate", ""
            ),
            "metadata_assignment": "NOT_ASSIGNED",
        })

    # Save a separate report; no database records are changed.
    fieldnames = list(report[0].keys()) if report else []

    with OUTPUT_FILE.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report)

    status_counts = Counter(
        row["verification_status"] for row in catalogue_rows
    )

    print("V3 metadata audit completed.")
    print(f"Extracted pages: {len(extracted_pages)}")
    print(f"Page-index rows: {len(index_rows)}")
    print(f"Catalogue records: {len(catalogue_rows)}")
    print(
        "Catalogue source pages found in extracted text:",
        sum(row["source_page_exists"] for row in report),
    )
    print(
        "Source pages where the index detects the exact course code:",
        sum(row["index_detected_course_code"] for row in report),
    )
    print("\nCatalogue verification statuses:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    print(f"\nReport saved to: {OUTPUT_FILE}")
    print("No ChromaDB records were changed.")
    print("No course or semester metadata was assigned.")


if __name__ == "__main__":
    main()
