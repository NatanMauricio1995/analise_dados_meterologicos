
from sqlalchemy import select
from sqlalchemy.orm import Session

from entities.ponto_observacao import PontoObservacao


class PontoObservacaoRepository:

    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_todos(self) -> list[PontoObservacao]:
        consulta = select(PontoObservacao).order_by(PontoObservacao.ponto_observacao_id)

        return list(self.sessao.scalars(consulta).all())

    def buscar_por_id(self, ponto_observacao_id: int) -> PontoObservacao | None:
        return self.sessao.get(PontoObservacao, ponto_observacao_id)

    def criar(self, dados: dict) -> PontoObservacao:
        ponto = PontoObservacao(**dados)

        self.sessao.add(ponto)
        self.sessao.flush()

        return ponto

    def atualizar(self, ponto: PontoObservacao, dados: dict) -> PontoObservacao:
        for campo, valor in dados.items():
            setattr(ponto, campo, valor)

        self.sessao.flush()

        return ponto

    def excluir(self, ponto: PontoObservacao) -> None:
        self.sessao.delete(ponto)
        self.sessao.flush()
