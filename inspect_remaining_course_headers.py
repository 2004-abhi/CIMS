
import re
from pypdf import PdfReader

pdf_path = "data/cse_syllabus_2019_s1_s8.pdf"
reader = PdfReader(pdf_path)

pages = [
    849, 861, 872,
    911, 925, 936, 946, 955, 968, 980, 989, 1000,
    1009, 1019, 1032, 1037, 1048, 1062,
    1097, 1110, 1121, 1130, 1142, 1155, 1168, 1178,
    1188, 1197, 1209, 1217, 1230, 1240, 1251, 1261,
    1272, 1282, 1295, 1305, 1316, 1321
]

for page_no in pages:
    text = reader.pages[page_no - 1].extract_text() or ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    print(f"\n--- PDF PAGE {page_no} ---")

    # Print lines around the course code and category labels
    matches = [
        i for i, line in enumerate(lines)
        if re.search(r"\b(CATEGORY|COURSE NAME|COURSE CODE|CODE)\b", line, re.I)
        or re.search(r"\b(CSD|CST|HUT|MCN)\s*\d{3}\b", line, re.I)
        or re.search(r"\b(SEMESTER|MINOR|HONOURS|PCC|PEC|PWS|VAC|BSC|ESC|MNC)\b", line, re.I)
    ]

    shown = set()
    for i in matches:
        for j in range(max(0, i - 1), min(len(lines), i + 3)):
            if j not in shown:
                print(lines[j])
                shown.add(j)

print("\nInspection only. No files were modified.")
