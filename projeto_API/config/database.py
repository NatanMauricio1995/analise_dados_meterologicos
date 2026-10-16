import os

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Localiza o .env na raiz do projeto
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
    raise RuntimeError("Verifique as variáveis de conexão no arquivo . env")

# Monta a URL de conexão com o MySQL.
DATABASE_URL = (f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}" f"@{DB_HOST}:{DB_PORT}/{DB_NAME}" "?charset=utf8mb4")

# Configura o mecanismo de conexão.
engine = create_engine(DATABASE_URL, pool_pre_ping = True)