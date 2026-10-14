
import csv
from pathlib import Path

output_path = Path("data/verified_index_evidence.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

courses = [
    # Semester V — PDF page 490
    ("CST 301", "FORMAL LANGUAGES AND AUTOMATA THEORY", "V", "PCC", 490),
    ("CST 303", "COMPUTER NETWORKS", "V", "PCC", 490),
    ("CST 305", "SYSTEM SOFTWARE", "V", "PCC", 490),
    ("CST 307", "MICROPROCESSORS AND MICROCONTROLLERS", "V", "PCC", 490),
    ("CST 309", "MANAGEMENT OF SOFTWARE SYSTEMS", "V", "PCC", 490),
    ("CSL 331", "SYSTEM SOFTWARE AND MICROPROCESSORS LAB", "V", "PCC", 490),
    ("CSL 333", "DATABASE MANAGEMENT SYSTEMS LAB", "V", "PCC", 490),
    ("CST 381", "CONCEPTS IN SOFTWARE ENGINEERING", "V", "Minor", 490),
    ("CST 383", "CONCEPTS IN MACHINE LEARNING", "V", "Minor", 490),
    ("CST 385", "CLIENT SERVER SYSTEMS", "V", "Minor", 490),
    ("CST 393", "CRYPTOGRAPHIC ALGORITHMS", "V", "Honours", 490),
    ("CST 395", "NEURAL NETWORKS AND DEEP LEARNING", "V", "Honours", 490),
    ("CST 397", "PRINCIPLES OF MODEL CHECKING", "V", "Honours", 490),

    # Semester VI — PDF page 491
    ("CST 302", "COMPILER DESIGN", "VI", "PCC", 491),
    ("CST 304", "COMPUTER GRAPHICS AND IMAGE PROCESSING", "VI", "PCC", 491),
    ("CST 306", "ALGORITHM ANALYSIS AND DESIGN", "VI", "PCC", 491),
    ("CST 308", "COMPREHENSIVE COURSE WORK", "VI", "PCC", 491),
    ("CSL 332", "NETWORKING LAB", "VI", "PCC", 491),
    ("CSD 334", "MINI PROJECT", "VI", "PCC", 491),
    ("CST 312", "FOUNDATIONS OF MACHINE LEARNING", "VI", "PEC", 491),
    ("CST 322", "DATA ANALYTICS", "VI", "PEC", 491),
    ("CST 332", "FOUNDATIONS OF SECURITY IN COMPUTING", "VI", "PEC", 491),
    ("CST 342", "AUTOMATED VERIFICATION", "VI", "PEC", 491),
    ("CSL 362", "PROGRAMMING IN PYTHON", "VI", "PEC", 491),
    ("CST 372", "DATA AND COMPUTER COMMUNICATION", "VI", "PEC", 491),
    ("CST 382", "INTRODUCTION TO SOFTWARE TESTING", "VI", "Minor", 491),
    ("CST 384", "CONCEPTS IN DEEP LEARNING", "VI", "Minor", 491),
    ("CST 386", "WIRELESS NETWORKS AND IOT APPLICATIONS", "VI", "Minor", 491),
    ("CST 394", "NETWORK SECURITY", "VI", "Honours", 491),
    ("CST 396", "ADVANCED TOPICS IN MACHINE LEARNING", "VI", "Honours", 491),
    ("CST 398", "THEORY OF COMPUTABILITY AND COMPLEXITY", "VI", "Honours", 491),
]

with output_path.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow([
        "course_code",
        "course_title",
        "semester",
        "category",
        "evidence_pdf_page",
        "verification_status",
    ])

    for code, title, semester, category, page in courses:
        writer.writerow([
            code, title, semester, category, page,
            "Verified from curriculum index",
        ])

print(f"Created: {output_path}")
print(f"Courses recorded: {len(courses)}")
print("Source: 2019 Scheme syllabus curriculum index, PDF pages 490–491.")
