import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

# Localiza o arquivo .env na raiz do projeto.
RAIZ_PROJETO = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ_PROJETO / ".env")

# Lê as configurações da conexão.
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Confere se as configurações obrigatórias existem.
if not all([DB_HOST, DB_NAME, DB_USER]) or DB_PASSWORD is None:
    raise RuntimeError("Verifique as variáveis de conexão no arquivo .env.")

# Monta a URL de conexão com o MySQL.
DATABASE_URL = URL.create(drivername="mysql+pymysql", username=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=int(DB_PORT), database=DB_NAME, query={"charset": "utf8mb4"},)

# Configura o mecanismo de conexão.
engine = create_engine(DATABASE_URL, pool_pre_ping=True,)

# Cria a fábrica de sessões para as consultas ao banco.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)
