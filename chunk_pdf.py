from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# PDF location
pdf_path = "data/cse_syllabus_2019_s1_s8.pdf"


# Read the PDF
reader = PdfReader(pdf_path)


# Store all extracted text
full_text = ""

for page in reader.pages:
    text = page.extract_text()

    if text:
        full_text += text + "\n"


print("Total characters:", len(full_text))


# Create the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


# Split the text
chunks = text_splitter.split_text(full_text)


print("Total chunks:", len(chunks))


# Display first 5 chunks
for i, chunk in enumerate(chunks[:5]):

    print("\n" + "=" * 60)
    print("CHUNK", i + 1)
    print("=" * 60)

    print(chunk)