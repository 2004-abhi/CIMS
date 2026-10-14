
import csv
from pathlib import Path

courses = [
    # Semester III
    ["MAT 203", "DISCRETE MATHEMATICAL STRUCTURES", "III", "", "213"],
    ["CST 201", "DATA STRUCTURES", "III", "", "224"],
    ["CST 203", "LOGIC SYSTEM DESIGN", "III", "", "235"],
    ["CST 205", "OBJECT ORIENTED PROGRAMMING USING JAVA", "III", "", "246"],
    ["CSL 201", "DATA STRUCTURES LAB", "III", "", "258"],
    ["CSL 203", "OBJECT ORIENTED PROGRAMMING LAB (IN JAVA)", "III", "", "266"],
    ["CST 281", "OBJECT ORIENTED PROGRAMMING", "III", "", "273"],
    ["CST 283", "PYTHON FOR MACHINE LEARNING", "III", "", "285"],
    ["CST 285", "DATA COMMUNICATION", "III", "", "296"],

    # Semester IV
    ["MAT 206", "GRAPH THEORY", "IV", "", "307"],
    ["CST 202", "COMPUTER ORGANIZATION AND ARCHITECTURE", "IV", "", "322"],
    ["CST 204", "DATABASE MANAGEMENT SYSTEMS", "IV", "", "334"],
    ["CST 206", "OPERATING SYSTEMS", "IV", "", "349"],
    ["CSL 202", "DIGITAL LAB", "IV", "", "359"],
    ["CSL 204", "OPERATING SYSTEMS LAB", "IV", "", "364"],
    ["CST 282", "PROGRAMMING METHODOLOGIES", "IV", "", "370"],
    ["CST 284", "MATHEMATICS FOR MACHINE LEARNING", "IV", "", "381"],
    ["CST 286", "INTRODUCTION TO COMPUTER NETWORKS", "IV", "", "396"],
    ["CST 294", "COMPUTATIONAL FUNDAMENTALS FOR MACHINE LEARNING", "IV", "", "418"],
    ["CST 296", "PRINCIPLES OF PROGRAM ANALYSIS AND VERIFICATION", "IV", "", "435"],
    ["MCN 201", "SUSTAINABLE ENGINEERING", "IV", "", "448"],
    ["HUT 200", "PROFESSIONAL ETHICS", "IV", "", "484"],
    ["MCN 202", "CONSTITUTION OF INDIA", "IV", "", "469"],
]

output = Path("data/sem3_sem4_course_evidence.csv")
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "course_code",
        "course_title",
        "semester",
        "category",
        "source_pages",
    ])
    writer.writerows(courses)

print("Created:", output)
print("Evidence records:", len(courses))
print("Semester III:", sum(r[2] == "III" for r in courses))
print("Semester IV:", sum(r[2] == "IV" for r in courses))
print("Categories intentionally left unconfirmed.")
print("Main catalogue and ChromaDB were not modified.")

