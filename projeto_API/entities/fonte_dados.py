from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import Base

class FonteDados(Base):
    __tablename__ = "fonte_dados"

    fonte_dados_id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)

    nome: Mapped[str] = mapped_column(String(100), nullable = False)

    tipo: Mapped[str] = mapped_column(String(50), nullable = False)

    descricao : Mapped[str | None] = mapped_column(String(255), nullable = True)

    registros : Mapped[list["RegistroMeteorologico"]] = relationship(back_populates = "fonte_dados")