from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import ollama_mei_solver as mei
import traceback

# Asegúrate de importar tu clase CloudQuestionSolver correctamente

app = Flask(__name__)
CORS(app)  # Por si quieres permitir peticiones desde frontends o herramientas externas

solver = mei.CloudQuestionSolver()

@app.route("/solve", methods=["POST"])
def solve():
    try:
        data = request.get_json()

        if not data or 'question' not in data or 'type' not in data:
            return jsonify({"error": "Missing required fields: 'question' and 'type'"}), 400

        result = solver.solve_question(data)
        return jsonify(result), 200

    except Exception as e:
        traceback.print_exc()  # 🌋 Esto mostrará el error exacto en la terminal
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "✨ CloudQuestionSolver API is alive and flirting 💖"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
