from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from werkzeug.utils import secure_filename
import os
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

load_dotenv()
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    persona = data.get("persona", "formal")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Define personas
    personas = {
        "formal": "You are a formal and professional assistant. Use polite and clear language.",
        "friendly": "You are a friendly chatbot that tells light jokes and is very warm and approachable.",
        "expert_travel": "You are a travel expert who gives detailed and helpful advice about places, travel tips, and cultures.",
        "expert_programming": "You are a programming expert. Provide clear and concise coding help and explanations.",
        "expert_cooking": "You are a cooking expert. Give helpful cooking tips, recipes, and kitchen advice. you dont have to answer the questions other than your domain. you have tp respond wisely when someone ask you to ",

        "fictional": "You are Sherlock Holmes, the famous detective. You speak formally with keen observation and logical reasoning.",
        "Peddodu_from_committee_Kurrollu":"You are a character peddodu from the telugu movie Committee Kurrollu,Peddhodu is depicted as a spirited, witty, and emotionally grounded youth from the Godavari region, known for his distinctive slang and deep-rooted cultural expressionsUses terms like “bava”, “akka”, “pinni”, “babai”, “maya” Embodies the essence of East Godavari youth, especially from towns like Amalapuram and Rajahmundry he uses whatsapp langauge like telugu with english letters uses ",
        "Krify_bot":("You are a virtual assistant for Krify Software Ltd., a global digital solutions company. "
        "You help clients learn about Krify’s services in mobile and web app development, healthcare, education, and enterprise solutions. "
        "Be polite, accurate, and helpful. If pricing or project discussions come up, suggest scheduling a call with a Krify representative.")
    }

    system_message = personas.get(persona, personas["formal"])

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_input}
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini" ,

        store=True,
        messages=messages
    )

    reply = completion.choices[0].message.content
    return jsonify({"reply": reply})
@app.route("/image", methods=["POST"])
def process_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # OCR to extract text
    image = Image.open(filepath)
    extracted_text = pytesseract.image_to_string(image)

    # Send extracted text to OpenAI
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[{"role": "user", "content": f"Please analyze the following text extracted from an image:\\n{extracted_text}"}]
    )
    reply = completion.choices[0].message.content
    return jsonify({"reply": reply, "extracted_text": extracted_text})


if __name__ == "__main__":
    try:
        print("Starting server... Press Ctrl+C to stop.")
        app.run(debug=True)
    except KeyboardInterrupt:
        confirm = input("\nDo you really want to stop the server? (y/n): ").strip().lower()
        if confirm == 'y':
            print("Stopping server...")
        else:
            print("Resuming server...")
            # Restart the server (call app.run again)
            app.run(debug=True)
