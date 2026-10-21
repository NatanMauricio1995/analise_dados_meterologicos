from sqlalchemy import Integer, String, Numeric, CheckConstraint
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import Base

class PontoObservacao(Base): # Define uma classe que herda a configuração declarativa do SQLAlchemy.
    __tablename__ = "ponto_observacao" # Indica que a classe representa a tabela ponto_observacao.

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name = "ck_ponto_latitude"),

        CheckConstraint("longitude BETWEEN -180 AND 180", name = "ck_ponto_longitude")
    )

    ponto_observacao_id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)

    nome: Mapped[str] = mapped_column(String(100), nullable = False)

    latitude: Mapped[Decimal] = mapped_column(Numeric(9,6), nullable = False)

    longitude: Mapped[Decimal] = mapped_column(Numeric(9,6), nullable = False)

    cidade: Mapped[str | None] = mapped_column(String(100), nullable = True)

    estado: Mapped[str | None] = mapped_column(String(2), nullable = True)

    registros: Mapped[list["RegistroMeteorologico"]] = relationship(back_populates = "ponto_observacao")