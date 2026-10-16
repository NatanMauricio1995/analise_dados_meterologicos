from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from entities.base import base

class RegistroMeteorologico(Base):
    __tablename__ = "registro_meteorologico"

    registro_meteorologico_id : Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)

    ponto_observacao_id : Mapped[int] = mapped_column(Integer, ForeignKey("ponto_observacao.ponto_observacao_id"), nullable = False)

    fonte_dados_id : Mapped[int] = mapped_column(Integer, ForeignKey("fonte_dados.fonte_dados.id"), nullable = False)

    data_hora : Mapped[datetime] = mapped_column(DateTime, nullable = False)

    temperatura : Mapped[Decimal] = mapped_column(Numeric(5,2), nullable = False)

    umidade : Mapped[Decimal] = mapped_column(Numeric(5,2), nullable = False)

    precipitacao : Mapped[Decimal] = mapped_column(Numeric(8,2), nullable = False)

    ponto_observacao: Mapped["PontoObservacao"] = relationship(back_populates = "registros")

    fonte_dados: Mapped["FonteDados"] = relationship(back_populates = "registros")

