async function sendMessage() {

    const input = document.getElementById("messageInput");

    const message = input.value.trim();

    if (message === "") {
        return;
    }


    // Display user message
    addMessage(message, "user");


    // Clear input
    input.value = "";


    // Send message to Flask
    const response = await fetch("/predict", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: message
        })

    });


    // Get Flask response
    const data = await response.json();


    // Display bot response
    let botMessage = "";


    if (data.intent === "greeting") {
        botMessage = "Hello! 👋 How can I help you?";
    }

    else if (data.intent === "help") {
        botMessage = "Sure! I can help you with college-related information.";
    }

    else if (data.intent === "thanks") {
        botMessage = "You're welcome! 😊";
    }

    else if (data.intent === "goodbye") {
        botMessage = "Goodbye! Have a great day! 👋";
    }

    else if (data.intent === "document_query") {
        botMessage = "Sure! I can help you search the college documents.";
    }

    else if (data.intent === "information_query") {
        botMessage = "Sure! Please tell me what information you need.";
    }

    else {
        botMessage = "Sorry, I didn't understand that. Could you please try again?";
    }


    addMessage(botMessage, "bot");
}


function addMessage(message, type) {

    const chatBox = document.getElementById("chatBox");


    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message");


    if (type === "user") {
        messageDiv.classList.add("user-message");
    }

    else {
        messageDiv.classList.add("bot-message");
    }


    messageDiv.textContent = message;


    chatBox.appendChild(messageDiv);


    // Scroll to latest message
    chatBox.scrollTop = chatBox.scrollHeight;
}