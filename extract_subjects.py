
from pypdf import PdfReader
import re

pdf_path = "data/cse_syllabus_2019_s1_s8.pdf"
reader = PdfReader(pdf_path)

# Extract all PDF text
full_text = ""

for page in reader.pages:
    text = page.extract_text()
    if text:
        full_text += text + "\n"

# Locate Semester I and Semester II
start = re.search(r"\bSEMESTER\s+I\b", full_text, re.IGNORECASE)
end = re.search(r"\bSEMESTER\s+II\b", full_text, re.IGNORECASE)

if not start or not end or end.start() <= start.start():
    print("Could not locate the Semester I section.")
    raise SystemExit

semester_text = full_text[start.start():end.start()]

# Find course entries containing syllabus metadata
pattern = re.compile(
    r"\b([A-Z]{2,4}\s*\d{3})\b"
    r"([\s\S]{0,250}?)"
    r"CATEGORY\s+L\s*T\s*P\s+CREDITS?\b",
    re.IGNORECASE
)

subjects = {}

for match in pattern.finditer(semester_text):
    code = " ".join(match.group(1).upper().split())
    name = " ".join(match.group(2).split())

    # Remove leftover labels from extracted PDF text
    name = re.sub(r"^(?:COURSE\s+CODE\s*:?\s*)", "", name, flags=re.I)
    name = re.sub(r"^(?:COMPUTER SCIENCE AND ENGINEERING\s*)+", "", name, flags=re.I)
    name = name.strip(" :-\n")

    if name and len(name) > 3:
        subjects[code] = name

print("\nSEMESTER I — SUBJECT CANDIDATES")
print("=" * 50)

if subjects:
    for code, name in subjects.items():
        print(f"{code}: {name}")
    print("\nTotal unique candidates:", len(subjects))
else:
    print("No matching syllabus entries found.")
    print("The PDF formatting may require a different extraction pattern.")
