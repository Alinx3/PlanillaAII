from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

app = Flask(__name__)
CORS(app)

# ---------------- CONFIG ----------------

endpoint = "https://models.github.ai/inference"
model = "deepseek/DeepSeek-V3-0324"
token = os.environ["GITHUB_TOKEN"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

DATABASE_URL = "https://data-plantilla-default-rtdb.firebaseio.com"

HORARIOS = {
    "Lunes": ["14:00", "14:40", "15:30", "16:10", "17:00", "17:40", "18:20", "19:00"],
    "Martes": ["14:00", "14:40", "15:30", "16:10", "17:00", "17:40", "18:20"],
    "Miércoles": ["14:00", "14:40", "15:30", "16:10", "17:00", "17:40", "18:20", "19:00"],
    "Jueves": ["14:00", "14:40", "15:30", "16:10", "17:00", "17:40", "18:20"],
    "Viernes": ["14:00", "14:40", "15:30", "16:10", "17:00", "17:40", "18:20"]
}

# ---------------- FIREBASE ----------------

def obtener_tareas():
    try:
        r = requests.get(f"{DATABASE_URL}/notes.json", timeout=5)
        data = r.json()
        return data if data else {}
    except Exception:
        return {}

# ---------------- CHAT ----------------

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")
        tareas = obtener_tareas()

        system_prompt = f"""
Eres un asistente escolar.

Estos son los horarios:
{HORARIOS}

Estas son las tareas y exámenes:
{tareas}

Si el usuario pregunta por horarios, tareas, exámenes o actividades, usa esos datos.
Responde claro, útil y corto.
"""

        response = client.complete(
            messages=[
                SystemMessage(system_prompt),
                UserMessage(user_message),
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=500,
            model=model
        )

        reply = response.choices[0].message.content

        return jsonify({
            "reply": reply
        })

    except Exception as e:
        return jsonify({
            "reply": f"Error: {str(e)}"
        })

# ---------------- MAIN ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
