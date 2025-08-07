from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/humanize', methods=['POST'])
def humanize_text():
    data = request.get_json()
    texto = data.get('texto', '')
    humanizado = f"Hola! Aquí tienes tu texto humanizado:\n\n{texto}"
    return jsonify({'humanizado': humanizado})

@app.route('/summary', methods=['POST'])
def summarize_text():
    data = request.get_json()
    texto = data.get('texto', '')
    # Simple resumen: primeras 100 caracteres
    resumen = texto[:100] + ('...' if len(texto) > 100 else '')
    return jsonify({'resumen': resumen})

if __name__ == '__main__':
    app.run(debug=True)