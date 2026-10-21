from config.database import SessionLocal

def obter_sessao():
    return SessionLocal()

def encerrar_sessao(sessao):
    sessao.close()
