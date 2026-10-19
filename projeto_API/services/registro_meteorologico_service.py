
from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from entities.registro_meteorologico import RegistroMeteorologico
from repositories.registro_meteorologico_repository import (RegistroMeteorologicoRepository,)
from repositories.ponto_observacao_repository import (PontoObservacaoRepository,)
from repositories.fonte_dados_repository import FonteDadosRepository


class RegistroMeteorologicoService:

    def __init__(self, sessao: Session):
        self.sessao = sessao
        self.repositorio = RegistroMeteorologicoRepository(sessao)
        self.pontos = PontoObservacaoRepository(sessao)
        self.fontes = FonteDadosRepository(sessao)

    def listar_todos(self) -> list[RegistroMeteorologico]:
        return self.repositorio.listar_todos()

    def buscar_por_id(self, registro_meteorologico_id: int,) -> RegistroMeteorologico:
        registro = self.repositorio.buscar_por_id(registro_meteorologico_id)

        if registro is None:
            raise ValueError("Registro meteorológico não encontrado.")

        return registro

    def listar_por_ponto(self, ponto_observacao_id: int,) -> list[RegistroMeteorologico]:
        if self.pontos.buscar_por_id(ponto_observacao_id) is None:
            raise ValueError("Ponto de observação não encontrado.")

        return self.repositorio.listar_por_ponto(ponto_observacao_id)

    def listar_por_fonte(self, fonte_dados_id: int,) -> list[RegistroMeteorologico]:
        if self.fontes.buscar_por_id(fonte_dados_id) is None:
            raise ValueError("Fonte de dados não encontrada.")

        return self.repositorio.listar_por_fonte(fonte_dados_id)

    def criar(self, dados: dict) -> RegistroMeteorologico:
        dados = self._validar_dados(dados)

        try:
            registro = self.repositorio.criar(dados)
            self.sessao.commit()
            return registro

        except IntegrityError as erro:
            self.sessao.rollback()
            raise ValueError(
                "Os dados violam uma restrição do banco de dados. "
                "Verifique os relacionamentos e se já existe uma "
                "medição para a mesma fonte, ponto e data/hora."
            ) from erro

        except SQLAlchemyError:
            self.sessao.rollback()
            raise

    def atualizar(
        self,
        registro_meteorologico_id: int,
        dados: dict,
    ) -> RegistroMeteorologico:
        registro = self.buscar_por_id(registro_meteorologico_id)
        dados = self._validar_dados(dados, parcial=True)

        try:
            registro = self.repositorio.atualizar(registro, dados)
            self.sessao.commit()
            return registro

        except IntegrityError as erro:
            self.sessao.rollback()
            raise ValueError(
                "Os dados violam uma restrição do banco de dados."
            ) from erro

        except SQLAlchemyError:
            self.sessao.rollback()
            raise

    def excluir(self, registro_meteorologico_id: int) -> None:
        registro = self.buscar_por_id(registro_meteorologico_id)

        try:
            self.repositorio.excluir(registro)
            self.sessao.commit()

        except SQLAlchemyError:
            self.sessao.rollback()
            raise

    def _validar_dados(
        self,
        dados: dict,
        parcial: bool = False,
    ) -> dict:
        if not isinstance(dados, dict):
            raise ValueError("Os dados devem ser enviados como objeto.")

        campos_obrigatorios = {
            "ponto_observacao_id",
            "fonte_dados_id",
            "data_hora",
            "temperatura",
            "umidade",
            "precipitacao",
        }

        campos_permitidos = campos_obrigatorios

        if not parcial:
            faltantes = campos_obrigatorios - dados.keys()

            if faltantes:
                raise ValueError(
                    "Campos obrigatórios ausentes: "
                    + ", ".join(sorted(faltantes))
                    + "."
                )

        desconhecidos = dados.keys() - campos_permitidos

        if desconhecidos:
            raise ValueError(
                "Campos não permitidos: "
                + ", ".join(sorted(desconhecidos))
                + "."
            )

        dados = dados.copy()

        for campo, repositorio, mensagem in (
            (
                "ponto_observacao_id",
                self.pontos,
                "Ponto de observação não encontrado.",
            ),
            (
                "fonte_dados_id",
                self.fontes,
                "Fonte de dados não encontrada.",
            ),
        ):
            if campo not in dados:
                continue

            identificador = dados[campo]

            if (
                isinstance(identificador, bool)
                or not isinstance(identificador, int)
                or identificador <= 0
            ):
                raise ValueError(
                    f"O campo '{campo}' deve ser um inteiro positivo."
                )

            if repositorio.buscar_por_id(identificador) is None:
                raise ValueError(mensagem)

        if "data_hora" in dados:
            data_hora = dados["data_hora"]

            if isinstance(data_hora, str):
                try:
                    data_hora = datetime.fromisoformat(data_hora)
                except ValueError as erro:
                    raise ValueError(
                        "A data/hora deve estar em formato ISO 8601, "
                        "por exemplo: 2026-10-19T14:30:00."
                    ) from erro

            if not isinstance(data_hora, datetime):
                raise ValueError(
                    "O campo 'data_hora' deve ser uma data/hora válida."
                )

            if data_hora.tzinfo is not None:
                raise ValueError(
                    "A data/hora deve ser informada sem fuso horário."
                )

            dados["data_hora"] = data_hora

        limites = {
            "temperatura": (Decimal("-90"), Decimal("60")),
            "umidade": (Decimal("0"), Decimal("100")),
            "precipitacao": (Decimal("0"), Decimal("999999.99")),
        }

        for campo, (minimo, maximo) in limites.items():
            if campo not in dados:
                continue

            valor = dados[campo]

            if isinstance(valor, bool):
                raise ValueError(
                    f"O campo '{campo}' deve ser numérico."
                )

            try:
                valor = Decimal(str(valor))
            except (InvalidOperation, ValueError, TypeError) as erro:
                raise ValueError(
                    f"O campo '{campo}' deve ser numérico."
                ) from erro

            if not valor.is_finite():
                raise ValueError(
                    f"O campo '{campo}' deve ser um número finito."
                )

            if not minimo <= valor <= maximo:
                raise ValueError(
                    f"O campo '{campo}' deve estar entre "
                    f"{minimo} e {maximo}."
                )

            if valor.as_tuple().exponent < -2:
                raise ValueError(
                    f"O campo '{campo}' aceita no máximo "
                    "duas casas decimais."
                )

            dados[campo] = valor

        return dados
