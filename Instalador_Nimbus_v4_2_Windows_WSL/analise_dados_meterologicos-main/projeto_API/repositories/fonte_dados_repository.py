
from sqlalchemy import select
from sqlalchemy.orm import Session

from entities.fonte_dados import FonteDados


class FonteDadosRepository:

    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_todos(self) -> list[FonteDados]:
        consulta = select(FonteDados).order_by(FonteDados.fonte_dados_id)

        return list(self.sessao.scalars(consulta).all())

    def buscar_por_id(self, fonte_dados_id: int) -> FonteDados | None:
        return self.sessao.get(FonteDados, fonte_dados_id)

    def criar(self, dados: dict) -> FonteDados:
        fonte = FonteDados(**dados)

        self.sessao.add(fonte)
        self.sessao.flush()

        return fonte

    def atualizar(self, fonte: FonteDados, dados: dict) -> FonteDados:
        for campo, valor in dados.items():
            setattr(fonte, campo, valor)

        self.sessao.flush()

        return fonte

    def excluir(self, fonte: FonteDados) -> None:
        self.sessao.delete(fonte)
        self.sessao.flush()
