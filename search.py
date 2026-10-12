
import chromadb
from sentence_transformers import SentenceTransformer


# ==========================================
# 1. LOAD THE EMBEDDING MODEL
# ==========================================

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")


# ==========================================
# 2. CONNECT TO CHROMADB
# ==========================================

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="cims_syllabus_v2"
)

print("ChromaDB connected!")
print("Stored chunks:", collection.count())


# ==========================================
# 3. MAT 101 SYLLABUS FROM THE PDF
# ==========================================

MAT101_MODULES = {
    1: {
        "title": "Linear Algebra",
        "hours": 10,
        "topics": [
            "Systems of linear equations",
            "Solution by Gauss elimination",
            "Row echelon form",
            "Finding rank from row echelon form",
            "Fundamental theorem for linear systems",
            "Eigenvalues and eigenvectors",
            "Diagonalization of matrices",
            "Orthogonal transformation",
            "Quadratic forms and their canonical forms"
        ]
    },

    2: {
        "title": "Multivariable Calculus - Differentiation",
        "hours": 8,
        "topics": [
            "Limits and continuity of functions of two variables",
            "Partial derivatives",
            "Differentials",
            "Local linear approximations",
            "Chain rule",
            "Total derivative",
            "Maxima and minima"
        ]
    },

    3: {
        "title": "Multivariable Calculus - Integration",
        "hours": 10,
        "topics": [
            "Evaluation of double integrals in Cartesian coordinates",
            "Change of order of integration in double integrals",
            "Change of coordinates from Cartesian to polar",
            "Finding areas and volumes",
            "Mass and centre of gravity of plane laminas",
            "Triple integrals"
        ]
    },

    4: {
        "title": "Sequences and Series",
        "hours": 8,
        "topics": [
            "Convergence of sequences and series",
            "Geometric series and p-series",
            "Comparison test",
            "Ratio test",
            "Root test",
            "Alternating series and Leibnitz test",
            "Absolute and conditional convergence"
        ]
    },

    5: {
        "title": "Series Representation of Functions",
        "hours": 9,
        "topics": [
            "Taylor series",
            "Binomial series",
            "Series representation of exponential functions",
            "Series representation of trigonometric functions",
            "Series representation of logarithmic functions",
            "Fourier series",
            "Euler formulas",
            "Convergence of Fourier series and Dirichlet's conditions",
            "Half-range sine and cosine series",
            "Parseval's theorem"
        ]
    }
}


MAT101_OUTCOMES = [
    "CO1: Solve systems of linear equations, diagonalize matrices "
    "and characterise quadratic forms.",

    "CO2: Compute partial and total derivatives and maxima and "
    "minima of multivariable functions.",

    "CO3: Compute multiple integrals and apply them to find areas, "
    "volumes, mass and centre of gravity of plane laminas.",

    "CO4: Perform tests to determine whether a series is convergent, "
    "absolutely convergent or conditionally convergent.",

    "CO5: Determine Taylor and Fourier series expansions of functions "
    "and learn their applications."
]


# ==========================================
# 4. COURSE-SPECIFIC SEARCH
# ==========================================

def format_module(number):
    module = MAT101_MODULES[number]

    result = [
        f"MAT 101 - {module['title']}",
        f"Module {number}",
        f"Lecture hours: {module['hours']}",
        "",
        "Topics:"
    ]

    for topic in module["topics"]:
        result.append(f"- {topic}")

    return "\n".join(result)


def search_mat101(question):
    question_lower = question.lower()

    # Match explicit module references
    module_number = None

    for number in range(1, 6):
        patterns = [
            f"module {number}",
            f"module-{number}",
            f"module{number}",
            f"module {number_in_words(number)}"
        ]

        if any(pattern in question_lower for pattern in patterns):
            module_number = number
            break

    if module_number is not None:
        return format_module(module_number)

    # Return all five modules for a full syllabus question
    syllabus_keywords = [
        "syllabus",
        "all modules",
        "all topics",
        "course contents",
        "full syllabus",
        "complete syllabus"
    ]

    mathematics_keywords = [
        "mat 101",
        "mat101",
        "engineering mathematics",
        "linear algebra and calculus",
        "linear algebra & calculus"
    ]

    is_math_question = any(
        keyword in question_lower
        for keyword in mathematics_keywords
    )

    asks_full_syllabus = any(
        keyword in question_lower
        for keyword in syllabus_keywords
    )

    if is_math_question and asks_full_syllabus:
        sections = [
            "MAT 101 - LINEAR ALGEBRA AND CALCULUS",
            "Course outcomes:",
            *MAT101_OUTCOMES,
            "",
            "MODULE SYLLABUS"
        ]

        for number in range(1, 6):
            sections.append("")
            sections.append(format_module(number))

        sections.append("")
        sections.append(
            "Total scheduled lecture hours: 45"
        )

        return "\n".join(sections)

    # Match questions about course outcomes
    if (
        is_math_question
        and (
            "course outcome" in question_lower
            or "learning outcome" in question_lower
        )
    ):
        return (
            "MAT 101 - Course Outcomes\n\n"
            + "\n".join(MAT101_OUTCOMES)
        )

    return None


def number_in_words(number):
    words = {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five"
    }
    return words[number]


# ==========================================
# 5. CHROMADB SEMANTIC SEARCH
# ==========================================

def search_chromadb(question, top_k=5):

    count = collection.count()

    if count == 0:
        return "No syllabus documents are stored in ChromaDB."

    question_embedding = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, count),
        include=["documents", "distances"]
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        return "Sorry, no syllabus information was found."

    print("\n========== CHROMADB SEARCH RESULTS ==========")

    relevant_documents = []

    for index, (document, distance) in enumerate(
        zip(documents, distances), start=1
    ):
        print(f"\nResult {index}")
        print(f"Distance: {distance:.4f}")
        print(document[:500])
        print("-" * 50)

        relevant_documents.append(document)

    return "\n\n".join(relevant_documents)


# ==========================================
# 6. MAIN SEARCH FUNCTION
# ==========================================

def search_syllabus(question, top_k=5):

    question = question.strip()

    if not question:
        return "Please enter a question."

    # Try the known MAT 101 syllabus first
    course_answer = search_mat101(question)

    if course_answer is not None:
        print("\nUsing course-specific MAT 101 syllabus.")
        return course_answer

    # Fall back to semantic search for other subjects
    return search_chromadb(question, top_k)


# ==========================================
# 7. TEST SEARCH INDEPENDENTLY
# ==========================================

if __name__ == "__main__":

    print("\nCIMS Syllabus Search")
    print("-------------------")

    while True:

        question = input(
            "\nEnter your syllabus question (or type 'exit'): "
        ).strip()

        if question.lower() == "exit":
            print("Search closed.")
            break

        answer = search_syllabus(question)

        print("\n========== RETRIEVED SYLLABUS ==========")
        print(answer)
