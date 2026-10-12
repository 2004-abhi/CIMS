
from flask import Flask, request, jsonify, render_template
import joblib
import json

app = Flask(__name__)

# Load the trained intent model
model = joblib.load("intent/model/intent_model.pkl")
vectorizer = joblib.load("intent/model/tfidf_vectorizer.pkl")

# Load structured subject data
with open("data/subjects.json", "r", encoding="utf-8") as file:
    subjects_data = json.load(file)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"response": "Please enter a question."}), 400

    # Answer semester-subject questions using exact structured data
    normalized_message = message.lower()

    semester_keywords = [
        "semester 1",
        "semester i",
        "first semester",
        "sem 1",
        "s1"
    ]

    subject_keywords = ["subject", "subjects", "course", "courses"]

    if (
        any(keyword in normalized_message for keyword in semester_keywords)
        and any(keyword in normalized_message for keyword in subject_keywords)
    ):
        subjects = subjects_data.get("semester_1", [])

        answer = "Semester 1 subjects:\n" + "\n".join(
            f"{subject['code']} - {subject['name']}"
            for subject in subjects
        )

        return jsonify({
            "message": message,
            "intent": "semester_subject_query",
            "response": answer
        })

    # Use the existing intent classifier for other questions
    X = vectorizer.transform([message])
    prediction = model.predict(X)[0]

    responses = {
        "greeting": "Hello! How can I help you?",
        "help": "I can help with college information and syllabus questions.",
        "thanks": "You're welcome!",
        "goodbye": "Goodbye! Have a great day!",
        "document_query": "Document search will be connected next.",
        "information_query": "Please tell me what college information you need.",
        "unknown": "Sorry, I couldn't understand your question."
    }

    return jsonify({
        "message": message,
        "intent": prediction,
        "response": responses.get(
            prediction,
            "Sorry, I couldn't understand your question."
        )
    })


if __name__ == "__main__":
    app.run(debug=True)
