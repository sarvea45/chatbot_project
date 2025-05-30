const chatBody = document.getElementById("chat-body");
const input = document.getElementById("user-input");
const personaSelect = document.getElementById("persona");
const imageInput = document.getElementById("imageInput");

// Add a new chat message
function addMessage(text, sender = "bot") {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.innerText = text;
  chatBody.appendChild(msg);
  chatBody.scrollTop = chatBody.scrollHeight;
}

// Handle text message sending
async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  const loading = document.createElement("div");
  loading.className = "message bot";
  loading.innerText = "Typing...";
  chatBody.appendChild(loading);
  chatBody.scrollTop = chatBody.scrollHeight;

  const persona = personaSelect.value;

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, persona })
    });

    const data = await response.json();
    loading.remove();
    addMessage(data.reply, "bot");
  } catch (err) {
    loading.remove();
    addMessage("❌ Error: Unable to reach chatbot.", "bot");
  }
}

// Handle Enter key
input.addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    event.preventDefault();
    sendMessage();
  }
});

// Handle image upload + OCR + GPT
imageInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("image", file);

  addMessage("📷 Uploading image and extracting text...", "user");

  const loading = document.createElement("div");
  loading.className = "message bot";
  loading.innerText = "Analyzing image...";
  chatBody.appendChild(loading);

  fetch("/image", {
    method: "POST",
    body: formData
  })
    .then((res) => res.json())
    .then((data) => {
      loading.remove();
      addMessage("🤖 Bot says:\n" + data.reply, "bot");
    })
    .catch(() => {
      loading.remove();
      addMessage("❌ Failed to process image.", "bot");
    });
});
