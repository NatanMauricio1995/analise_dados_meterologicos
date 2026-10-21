
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from entities.registro_meteorologico import RegistroMeteorologico


class RegistroMeteorologicoRepository:

    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_todos(self) -> list[RegistroMeteorologico]:
        consulta = select(RegistroMeteorologico).order_by(RegistroMeteorologico.data_hora, RegistroMeteorologico.registro_meteorologico_id)

        return list(self.sessao.scalars(consulta).all())

    def buscar_por_id(self, registro_meteorologico_id: int) -> RegistroMeteorologico | None:
        return self.sessao.get(RegistroMeteorologico, registro_meteorologico_id)

    def listar_por_ponto(self, ponto_observacao_id: int) -> list[RegistroMeteorologico]:
        consulta = (select(RegistroMeteorologico).where(RegistroMeteorologico.ponto_observacao_id == ponto_observacao_id).order_by(RegistroMeteorologico.data_hora))

        return list(self.sessao.scalars(consulta).all())

    def listar_por_fonte(self, fonte_dados_id: int) -> list[RegistroMeteorologico]:
        consulta = (select(RegistroMeteorologico).where(RegistroMeteorologico.fonte_dados_id == fonte_dados_id).order_by(RegistroMeteorologico.data_hora))

        return list(self.sessao.scalars(consulta).all())

    def criar(self, dados: dict) -> RegistroMeteorologico:
        registro = RegistroMeteorologico(**dados)

        self.sessao.add(registro)
        self.sessao.flush()

        return registro

    def atualizar(self, registro: RegistroMeteorologico, dados: dict) -> RegistroMeteorologico:
        for campo, valor in dados.items():
            setattr(registro, campo, valor)

        self.sessao.flush()

        return registro

    def excluir(self, registro: RegistroMeteorologico) -> None:
        self.sessao.delete(registro)
        self.sessao.flush()
