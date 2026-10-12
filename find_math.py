
from pypdf import PdfReader

pdf_path = "data/cse_syllabus_2019_s1_s8.pdf"
reader = PdfReader(pdf_path)

# Print PDF pages 8 to 10 to inspect the complete course schedule
for page_number in range(8, 11):
    page_text = reader.pages[page_number - 1].extract_text() or ""

    print("\n" + "=" * 60)
    print("PDF PAGE:", page_number)
    print("=" * 60)
    print(page_text)
