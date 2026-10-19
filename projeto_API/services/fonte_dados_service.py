
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from entities.fonte_dados import FonteDados
from repositories.fonte_dados_repository import FonteDadosRepository


class FonteDadosService:

    def __init__(self, sessao: Session):
        self.sessao = sessao
        self.repositorio = FonteDadosRepository(sessao)

    def listar_todos(self) -> list[FonteDados]:
        return self.repositorio.listar_todos()

    def buscar_por_id(self, fonte_dados_id: int) -> FonteDados:
        fonte = self.repositorio.buscar_por_id(fonte_dados_id)

        if fonte is None:
            raise ValueError("Fonte de dados não encontrada.")

        return fonte

    def criar(self, dados: dict) -> FonteDados:
        dados = self._validar_dados(dados)

        try:
            fonte = self.repositorio.criar(dados)
            self.sessao.commit()
            return fonte

        except IntegrityError as erro:
            self.sessao.rollback()
            raise ValueError("Os dados violam uma restrição do banco de dados.") from erro

        except SQLAlchemyError:
            self.sessao.rollback()
            raise

    def atualizar(self, fonte_dados_id: int, dados: dict) -> FonteDados:
        fonte = self.buscar_por_id(fonte_dados_id)
        dados = self._validar_dados(dados, parcial=True)

        try:
            fonte = self.repositorio.atualizar(fonte, dados)
            self.sessao.commit()
            return fonte

        except IntegrityError as erro:
            self.sessao.rollback()
            raise ValueError("Os dados violam uma restrição do banco de dados.") from erro

        except SQLAlchemyError:
            self.sessao.rollback()
            raise

    def excluir(self, fonte_dados_id: int) -> None:
        fonte = self.buscar_por_id(fonte_dados_id)

        try:
            self.repositorio.excluir(fonte)
            self.sessao.commit()

        except IntegrityError as erro:
            self.sessao.rollback()
            raise ValueError("Não é possível excluir esta fonte porque existem registros meteorológicos associados.") from erro

        except SQLAlchemyError:
            self.sessao.rollback()
            raise

    def _validar_dados(self, dados: dict, parcial: bool = False) -> dict:
        if not isinstance(dados, dict):
            raise ValueError("Os dados devem ser enviados como objeto.")

        campos_obrigatorios = {"nome", "tipo", "descricao"}
        campos_permitidos = campos_obrigatorios

        if not parcial:
            faltantes = campos_obrigatorios - dados.keys()

            if faltantes:
                raise ValueError(
                    f"Campos obrigatórios ausentes: "
                    f"{', '.join(sorted(faltantes))}."
                )

        desconhecidos = dados.keys() - campos_permitidos

        if desconhecidos:
            raise ValueError(f"Campos não permitidos: " f"{', '.join(sorted(desconhecidos))}.")

        dados = dados.copy()

        for campo, limite in (("nome", 100), ("tipo", 50), ("descricao", 255)):
            if campo not in dados:
                continue

            valor = dados[campo]

            if valor is None and campo == "descricao":
                continue

            if not isinstance(valor, str):
                raise ValueError(f"O campo '{campo}' deve ser um texto.")

            valor = valor.strip()

            if campo != "descricao" and not valor:
                raise ValueError(f"O campo '{campo}' não pode ficar vazio.")

            if len(valor) > limite:
                raise ValueError(f"O campo '{campo}' deve ter no máximo " f"{limite} caracteres.")

            dados[campo] = valor

        return dados
