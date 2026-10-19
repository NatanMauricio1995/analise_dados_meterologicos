
from flask import Flask, jsonify
from flask_restful import Api

app = Flask(__name__)
api = Api(app)


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({
        "projeto": "Nimbus",
        "mensagem": "API de análise de dados meteorológicos",
        "status": "online"
    }), 200


@app.route("/health", methods=["GET"])
def verificar_saude():
    return jsonify({
        "status": "ok"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
