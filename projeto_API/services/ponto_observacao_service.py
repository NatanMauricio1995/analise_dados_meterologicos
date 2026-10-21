
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from decimal import Decimal, InvalidOperation
from sqlalchemy.orm import Session

from entities.estados import validar_estado
from entities.ponto_observacao import PontoObservacao
from repositories.ponto_observacao_repository import PontoObservacaoRepository

from exceptions.erros import RecursoNaoEncontradoError

class PontoObservacaoService:

    def __init__(self, sessao: Session):
        self.sessao = sessao
        self.repositorio = PontoObservacaoRepository(sessao)

    def listar_todos(self) -> list[PontoObservacao]:
        return self.repositorio.listar_todos()

    def buscar_por_id(self, ponto_observacao_id: int) -> PontoObservacao:
        ponto = self.repositorio.buscar_por_id(ponto_observacao_id)

        if ponto is None:
            raise RecursoNaoEncontradoError(
                "Ponto de observação não encontrado."
            )

        return ponto

    def criar(self, dados: dict) -> PontoObservacao:
        dados = self._validar_dados(dados)

        try:
            ponto = self.repositorio.criar(dados)
            self.sessao.commit()
            return ponto

        except IntegrityError as erro:
            self.sessao.rollback()
            raise ValueError("Os dados violam uma restrição do banco de dados.") from erro

        except SQLAlchemyError:
            self.sessao.rollback()
            raise

    def atualizar(self, ponto_observacao_id: int, dados: dict) -> PontoObservacao:
        ponto = self.buscar_por_id(ponto_observacao_id)
        dados = self._validar_dados(dados, parcial=True)

        try:
            ponto = self.repositorio.atualizar(ponto, dados)
            self.sessao.commit()
            return ponto

        except IntegrityError as erro:
            self.sessao.rollback()
            raise ValueError("Os dados violam uma restrição do banco de dados.") from erro

        except SQLAlchemyError:
            self.sessao.rollback()
            raise

    def excluir(self, ponto_observacao_id: int) -> None:
        ponto = self.buscar_por_id(ponto_observacao_id)

        try:
            self.repositorio.excluir(ponto)
            self.sessao.commit()

        except IntegrityError as erro:
            self.sessao.rollback()
            raise ValueError("Não é possível excluir este ponto porque existem registros meteorológicos associados.") from erro

        except SQLAlchemyError:
            self.sessao.rollback()
            raise

    def _validar_dados(self, dados: dict, parcial: bool = False) -> dict:
        if not isinstance(dados, dict):
            raise ValueError("Os dados devem ser enviados como objeto.")

        campos_obrigatorios = {"nome", "latitude", "longitude"}
        campos_permitidos = campos_obrigatorios | {"cidade", "estado"}

        if not parcial:
            faltantes = campos_obrigatorios - dados.keys()

            if faltantes:
                raise ValueError(f"Campos obrigatórios ausentes: {', '.join(sorted(faltantes))}.")

        desconhecidos = dados.keys() - campos_permitidos

        if desconhecidos:
            raise ValueError(f"Campos não permitidos: {', '.join(sorted(desconhecidos))}.")

        dados = dados.copy()

        for campo in ("nome", "cidade"):
            if campo in dados:
                valor = dados[campo]

                if campo == "cidade" and valor is None:
                    continue
                if not isinstance(valor, str) or (campo == "nome" and not valor.strip()):
                    raise ValueError(f"O campo '{campo}' deve ser um texto válido.")

                limite = 100

                if len(valor.strip()) > limite:
                    raise ValueError(f"O campo '{campo}' deve ter no máximo {limite} caracteres.")

                dados[campo] = valor.strip()

        if "estado" in dados:
            estado = dados["estado"]

            if estado is None or estado == "":
                dados["estado"] = None
                estado = None
            if estado is not None and not isinstance(estado, str):
                raise ValueError("O estado deve ser informado por uma sigla.")
            estado = estado.strip().upper() if estado is not None else None

            if estado is not None and not validar_estado(estado):
                raise ValueError("Informe uma sigla válida de estado brasileiro.")

            dados["estado"] = estado

        for campo, minimo, maximo in (("latitude", -90, 90),("longitude", -180, 180)):
            if campo in dados:
                valor = dados[campo]

                if isinstance(valor, bool):
                    raise ValueError(f"O campo '{campo}' deve ser numérico.")

                try:
                    valor = Decimal(str(valor).replace(",", "."))
                except (TypeError, ValueError, InvalidOperation) as erro:
                    raise ValueError(f"O campo '{campo}' deve ser numérico.") from erro

                if not valor.is_finite() or not Decimal(minimo) <= valor <= Decimal(maximo):
                    raise ValueError(f"O campo '{campo}' deve estar entre " f"{minimo} e {maximo}.")

                if valor != valor.quantize(Decimal("0.000001")):
                    raise ValueError(f"O campo '{campo}' aceita no máximo seis casas decimais.")
                dados[campo] = valor

        return dados
