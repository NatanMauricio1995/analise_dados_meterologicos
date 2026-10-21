"""Ponto de entrada da API Nimbus."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from flask import Flask, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config.database import SessionLocal
from routes.api_routes import api_bp


def create_app(session_factory=None):
    application = Flask(__name__)
    application.config["NIMBUS_SESSION_FACTORY"] = session_factory or SessionLocal
    application.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    application.register_blueprint(api_bp)

    @application.get("/")
    def index():
        return jsonify({"projeto": "Nimbus", "status": "online", "api": "/api"})

    @application.get("/health")
    def health():
        session = application.config["NIMBUS_SESSION_FACTORY"]()
        try:
            session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "banco": "conectado"}), 200
        except SQLAlchemyError:
            return jsonify({"status": "indisponivel", "banco": "sem conexao"}), 503
        finally:
            session.close()
    return application


app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
