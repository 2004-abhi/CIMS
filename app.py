from flask import Flask, request, jsonify, render_template
import joblib

app = Flask(__name__)


# Load the trained model
model = joblib.load("intent/model/intent_model.pkl")

# Load the TF-IDF vectorizer
vectorizer = joblib.load("intent/model/tfidf_vectorizer.pkl")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    # Get the JSON data sent by the user
    data = request.get_json()

    # Get the message
    message = data.get("message", "")

    # Convert message into TF-IDF features
    X = vectorizer.transform([message])

    # Predict the intent
    prediction = model.predict(X)[0]

    # Return the result
    return jsonify({
        "message": message,
        "intent": prediction
    })


if __name__ == "__main__":
    app.run(debug=True)