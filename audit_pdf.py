
import csv
import re
import json
from pathlib import Path
from pypdf import PdfReader

PDF_PATH = Path("data/cse_syllabus_2019_s1_s8.pdf")
OUTPUT_DIR = Path("data")

if not PDF_PATH.exists():
    raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

OUTPUT_DIR.mkdir(exist_ok=True)

reader = PdfReader(str(PDF_PATH))

inventory_path = OUTPUT_DIR / "pdf_page_inventory.csv"
full_text_path = OUTPUT_DIR / "pdf_full_text.jsonl"

# Candidate course-code pattern. These are candidates, not verified courses.
course_code_pattern = re.compile(
    r"\b(?:MAT|CST|CSL|CSD|CSQ|EST|ESL|PHT|PHL|CYT|CYL|"
    r"HUN|HUT|MCN|MCT|PEC|PCC|OEC|VAC|UK|ITT)\s*\d{3}\b",
    re.IGNORECASE
)

semester_pattern = re.compile(
    r"\b(?:semester|sem)\s*[-:]?\s*[1-8]\b",
    re.IGNORECASE
)

module_pattern = re.compile(
    r"\b(?:module|unit)\s*[-:]?\s*[1-6]\b",
    re.IGNORECASE
)

keywords = {
    "minor": re.compile(r"\bminor\b", re.IGNORECASE),
    "honours": re.compile(r"\bhonou?rs?\b", re.IGNORECASE),
    "exam": re.compile(
        r"\b(question paper|answer any|maximum marks|university examination)\b",
        re.IGNORECASE
    ),
    "regulation": re.compile(
        r"\b(regulation|curriculum|scheme of study)\b",
        re.IGNORECASE
    ),
    "project": re.compile(
        r"\b(mini project|project phase|project work)\b",
        re.IGNORECASE
    ),
    "lab": re.compile(r"\b(lab|laboratory|workshop)\b", re.IGNORECASE),
}

page_type_pattern = re.compile(
    r"\b(course code|course title|category|credit|syllabus|module)\b",
    re.IGNORECASE
)

with inventory_path.open("w", newline="", encoding="utf-8-sig") as csv_file, \
     full_text_path.open("w", encoding="utf-8") as text_file:

    writer = csv.DictWriter(
        csv_file,
        fieldnames=[
            "pdf_page",
            "text_length",
            "course_codes",
            "semester_mentions",
            "module_mentions",
            "minor",
            "honours",
            "exam_keywords",
            "regulation_keywords",
            "project_keywords",
            "lab_keywords",
            "needs_review",
            "preview",
        ],
    )
    writer.writeheader()

    total_chars = 0
    empty_pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        total_chars += len(text)

        if not text:
            empty_pages.append(page_number)

        codes = sorted({
            re.sub(r"\s+", " ", match.upper()).strip()
            for match in course_code_pattern.findall(text)
        })

        semester_mentions = sorted(set(semester_pattern.findall(text)))
        module_mentions = sorted(set(module_pattern.findall(text)))

        flags = {
            name: bool(pattern.search(text))
            for name, pattern in keywords.items()
        }

        writer.writerow({
            "pdf_page": page_number,
            "text_length": len(text),
            "course_codes": "; ".join(codes),
            "semester_mentions": "; ".join(semester_mentions),
            "module_mentions": "; ".join(module_mentions),
            "minor": flags["minor"],
            "honours": flags["honours"],
            "exam_keywords": flags["exam"],
            "regulation_keywords": flags["regulation"],
            "project_keywords": flags["project"],
            "lab_keywords": flags["lab"],
            "needs_review": bool(
                codes or any(flags.values()) or page_type_pattern.search(text)
            ),
            "preview": re.sub(r"\s+", " ", text)[:300],
        })

        # Preserve the complete extracted text, not just the preview.
        text_file.write(json.dumps({
            "pdf_page": page_number,
            "text": text,
        }, ensure_ascii=False) + "\n")

        if page_number % 100 == 0:
            print(f"Processed {page_number}/{len(reader.pages)} pages")

print("\nPDF audit completed.")
print(f"Total pages: {len(reader.pages)}")
print(f"Total extracted characters: {total_chars}")
print(f"Pages with no extractable text: {len(empty_pages)}")
if empty_pages:
    print("Pages to inspect manually:", empty_pages)

print(f"\nPage inventory: {inventory_path}")
print(f"Full extracted text: {full_text_path}")
print("\nImportant: keyword matches are candidates, not verified classifications.")
