from pypdf import PdfReader


# PDF file location
pdf_path = "data/cse_syllabus_2019_s1_s8.pdf"


# Read the PDF
reader = PdfReader(pdf_path)


print("Total pages:", len(reader.pages))


# Extract text from each page
for page_number, page in enumerate(reader.pages, start=1):

    text = page.extract_text()

    print("\n" + "=" * 60)
    print("PAGE", page_number)
    print("=" * 60)

    print(text)