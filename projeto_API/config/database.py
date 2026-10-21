"""Configuração SQLAlchemy: MySQL em produção, URL injetável em testes."""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
DATABASE_URL = os.getenv("NIMBUS_DATABASE_URL")
if not DATABASE_URL:
    required = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    if any(os.getenv(key) is None for key in required):
        raise RuntimeError("Configure DB_HOST, DB_NAME, DB_USER e DB_PASSWORD no .env.")
    DATABASE_URL = URL.create(
        "mysql+pymysql", username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "3306")), database=os.environ["DB_NAME"],
        query={"charset": "utf8mb4"},
    )
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
