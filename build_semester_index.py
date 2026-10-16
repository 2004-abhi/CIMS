
import csv
import json
import re
from pathlib import Path

INPUT_FILE = Path("data/pdf_full_text.jsonl")
OUTPUT_FILE = Path("data/semester_page_index.csv")
COURSE_OUTPUT = Path("data/course_heading_candidates.csv")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Missing {INPUT_FILE}. Run audit_pdf.py first."
    )

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Accept both Arabic and Roman semester numbering.
SEMESTER_RE = re.compile(
    r"\bSEMESTER\s*[-:]?\s*"
    r"(VIII|VII|VI|V|IV|III|II|I|[1-8])\b",
    re.IGNORECASE,
)

COURSE_CODE_RE = re.compile(
    r"\b(?:MAT|CST|CSL|CSD|CSQ|EST|ESL|PHT|PHL|CYT|CYL|"
    r"HUN|HUT|MCN|MCT|PEC|PCC|OEC|VAC|UK|ITT)\s*\d{3}\b",
    re.IGNORECASE,
)

def normalize_code(code):
    return re.sub(r"\s+", " ", code.upper()).strip()

def semester_number(value):
    value = value.upper()
    roman = {
        "I": 1, "II": 2, "III": 3, "IV": 4,
        "V": 5, "VI": 6, "VII": 7, "VIII": 8
    }
    return int(value) if value.isdigit() else roman[value]


def classify_page(text):
    upper = text.upper()

    # Identify question papers first
    if re.search(
        r"MODEL\s+QUESTION\s+PAPER|"
        r"SAMPLE\s+QUESTION\s+PAPER|"
        r"QUESTION\s+PAPER|"
        r"SCHEME\s+OF\s+VALUATION",
        upper,
    ):
        return "question_paper_or_valuation"

    # Identify pages with an explicit course heading
    has_course_code = bool(
        re.search(
            r"\b(?:MAT|CST|CSL|CSD|CSQ|EST|ESL|PHT|PHL|"
            r"CYT|CYL|HUN|HUT|MCN|MCT|PEC|PCC|OEC|VAC|UK|ITT)"
            r"\s*\d{3}\b",
            upper,
        )
    )

    has_course_details = (
        "CATEGORY" in upper
        and re.search(r"\bCREDIT(?:S)?\b", upper)
        and (
            "PREAMBLE" in upper
            or "COURSE OUTCOMES" in upper
        )
    )

    if has_course_code and has_course_details:
        return "likely_course_syllabus"

    if "PREAMBLE" in upper or "COURSE OUTCOMES" in upper:
        return "possible_syllabus_continuation"

    if re.search(r"\bREGULATION\b|\bSCHEME OF STUDY\b", upper):
        return "regulations_or_scheme"

    if re.search(r"\bMODULE\s*[-:]?\s*[1-6]\b", upper):
        return "possible_module_content"

    return "other_or_needs_review"


page_rows = []
course_rows = []

with INPUT_FILE.open(encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        page = record["pdf_page"]
        text = record.get("text", "")
        upper = text.upper()

        semester_matches = SEMESTER_RE.findall(text)
        semesters = sorted(
            {semester_number(s) for s in semester_matches}
        )

        codes = sorted({
            normalize_code(c)
            for c in COURSE_CODE_RE.findall(text)
        })

        flags = []
        if re.search(r"\bMINOR\b", upper):
            flags.append("Minor")
        if re.search(r"\bHONOU?RS?\b", upper):
            flags.append("Honours")
        if re.search(r"\bLAB(?:ORATORY)?\b|\bWORKSHOP\b", upper):
            flags.append("Lab/workshop")
        if re.search(r"\bPROJECT\b|\bSEMINAR\b", upper):
            flags.append("Project/seminar")

        category = classify_page(text)

        page_rows.append({
            "pdf_page": page,
            "text_length": len(text),
            "semester_heading_matches": "; ".join(map(str, semesters)),
            "course_codes": "; ".join(codes),
            "category_flags": "; ".join(flags),
            "page_type_candidate": category,
            "preview": re.sub(r"\s+", " ", text)[:250],
        })

        # Course headings require a code plus evidence of a syllabus table.
        # These are candidates only, not automatically verified courses.
        if codes and (
            "CATEGORY" in upper
            or "PREAMBLE" in upper
            or "COURSE OUTCOMES" in upper
        ):
            course_rows.append({
                "pdf_page": page,
                "course_codes": "; ".join(codes),
                "category_flags": "; ".join(flags),
                "page_type_candidate": category,
                "preview": re.sub(r"\s+", " ", text)[:500],
                "verified": False,
            })

def write_csv(path, rows):
    if not rows:
        print(f"No rows to write: {path}")
        return

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

write_csv(OUTPUT_FILE, page_rows)
write_csv(COURSE_OUTPUT, course_rows)

print("\nSemester indexing completed.")
print(f"Pages indexed: {len(page_rows)}")
print(f"Course-heading candidates: {len(course_rows)}")
print(f"Page index: {OUTPUT_FILE}")
print(f"Course candidates: {COURSE_OUTPUT}")
print("\nThese are candidates. Verify titles and semesters against the PDF.")
