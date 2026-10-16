from sqlalchemy import Integer, String, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import Base

class PontoObservacao(Base): # Define uma classe que herda a configuração declarativa do SQLAlchemy.
    __tablename__ = "ponto_observacao" # Indica que a classe representa a tabela ponto_observacao.

    __tableargs__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name = "ck_ponto_latitude"),

        CheckConstraint("longitude BETWEEN -180 AND 180", name = "ck_ponto_longitude")
    )

    ponto_observacao_id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)

    nome: Mapped[str] = mapped_column(String(100), nullable = False)

    latitude: Mapped[float] = mapped_column(Numeric(9,6), nullable = False)

    longitude: Mapped[float] = mapped_column(Numeric(9,6), nullable = False)

    cidade: Mapped[str] = mapped_column(String(100), nullable = False)

    estado: Mapped[str] = mapped_column(String(2), nullable = False)

    registros: Mapped[list["RegistroMeteorologico"]] = relationship(back_populates = "ponto_observacao")