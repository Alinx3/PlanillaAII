from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("OPENROUTER_API_KEY")
URL = "https://openrouter.ai/api/v1/chat/completions"

HORARIOS = {
    "Lunes": ["14:00", "14:40", "15:30", "16:10", "17:00", "17:40", "18:20", "19:00"],
    "Martes": ["14:00", "14:40", "15:30", "16:10", "17:00", "17:40", "18:20"],
    "Miércoles": ["14:00", "14:40", "15:30", "16:10", "17:00", "17:40", "18:20", "19:00"],
    "Jueves": ["14:00", "14:40", "15:30", "16:10", "17:00", "17:40", "18:20"],
    "Viernes": ["14:00", "14:40", "15:30", "16:10", "17:00", "17:40", "18:20"]
}

SYSTEM_PROMPT = f"""
Eres un asistente escolar.
Usa estos horarios si preguntan por clases:
{HORARIOS}

Responde claro y corto.
"""

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        r = requests.post(URL, headers=headers, json=data, timeout=20)
        result = r.json()

        if "choices" not in result:
            return jsonify({"reply": str(result)})

        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception:
        return jsonify({"reply": "No pude conectar con la IA."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
