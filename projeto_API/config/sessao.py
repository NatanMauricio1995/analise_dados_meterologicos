from config.database import SessionLocal


def obter_sessao():
    """Cria uma sessão SQLAlchemy para uso em uma requisição."""
    return SessionLocal()


def encerrar_sessao(sessao):
    """Encerra a sessão SQLAlchemy, liberando os recursos associados."""
    sessao.close()
