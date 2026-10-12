
console.log("CIMS JavaScript loaded!");

document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("messageInput");
    const sendButton = document.getElementById("sendButton");
    const chatBox = document.getElementById("chatBox");

    if (!input || !sendButton || !chatBox) {
        console.error("CIMS: HTML elements are missing!");
        return;
    }

    async function sendMessage() {

        const message = input.value.trim();

        if (message === "") {
            return;
        }

        addMessage(message, "user");
        input.value = "";
        sendButton.disabled = true;

        try {
            const response = await fetch("/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.response || "Request failed");
            }

            addMessage(
                data.response || "Sorry, I couldn't understand your question.",
                "bot"
            );

        } catch (error) {
            console.error("CIMS request error:", error);
            addMessage(
                "Unable to get a response. Check the server and Console.",
                "bot"
            );
        } finally {
            sendButton.disabled = false;
            input.focus();
        }
    }

    function addMessage(message, type) {

        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");

        if (type === "user") {
            messageDiv.classList.add("user-message");
        } else {
            messageDiv.classList.add("bot-message");
        }

        messageDiv.textContent = message;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    sendButton.addEventListener("click", sendMessage);

    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });

});
