
import re
import json
from pathlib import Path
from pypdf import PdfReader

PDF_PATH = Path("data/cse_syllabus_2019_s1_s8.pdf")
OUTPUT_PATH = Path("data/verified_courses.json")

reader = PdfReader(str(PDF_PATH))

# Match likely syllabus course headings, not category codes such as PCC 147.
course_pattern = re.compile(
    r"^\s*"
    r"(?P<code>"
    r"(?:MAT|CST|CSL|CSD|EST|ESL|PHT|PHL|CYT|CYL|"
    r"HUN|HUT|MCN|CSQ)"
    r"\s*\d{3}"
    r")\s+"
    r"(?P<title>.+?)\s*$",
    re.IGNORECASE
)

courses = {}

print("Scanning syllabus PDF for course headings...")

for page_number, page in enumerate(reader.pages, start=1):
    page_text = page.extract_text() or ""
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in page_text.splitlines()
        if line.strip()
    ]

    for index, line in enumerate(lines):
        match = course_pattern.match(line)

        if not match:
            continue

        code = re.sub(r"\s+", " ", match.group("code").upper())
        title = match.group("title").strip(" :-")

        # Ignore headings that clearly aren't course titles.
        if not title or title.isdigit():
            continue

        # Course entries should have a plausible title.
        if not re.search(r"[A-Za-z]{3,}", title):
            continue

        # Join the next line if the title appears incomplete.
        if (
            index + 1 < len(lines)
            and len(title.split()) <= 2
            and not re.match(r"^[A-Z]{2,}\s*\d{3}\b", lines[index + 1])
        ):
            next_line = lines[index + 1]
            if len(next_line) < 100:
                title = f"{title} {next_line}".strip()

        record = {
            "course_code": code,
            "course_title_candidate": title,
            "pdf_page": page_number,
            "scheme": "2019",
            "verified": False
        }

        # Keep each course code, with all pages where it appears.
        if code not in courses:
            courses[code] = {
                "course_code": code,
                "title_candidates": [],
                "pdf_pages": [],
                "scheme": "2019",
                "verified": False
            }

        if title not in courses[code]["title_candidates"]:
            courses[code]["title_candidates"].append(title)

        if page_number not in courses[code]["pdf_pages"]:
            courses[code]["pdf_pages"].append(page_number)

with OUTPUT_PATH.open("w", encoding="utf-8") as file:
    json.dump(
        list(courses.values()),
        file,
        indent=2,
        ensure_ascii=False
    )

print("\nScan completed.")
print("Course-code candidates:", len(courses))
print("Output saved to:", OUTPUT_PATH)
print("Note: candidates still require validation.")
