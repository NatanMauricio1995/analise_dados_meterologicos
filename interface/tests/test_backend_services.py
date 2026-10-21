"""Testes SQLAlchemy SQLite em memória; sem Docker/MySQL."""
import os
import sys
import unittest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'projeto_API'))
from entities import base, fonte_dados, ponto_observacao, registro_meteorologico  # noqa: F401
from services.fonte_dados_service import FonteDadosService
from services.ponto_observacao_service import PontoObservacaoService
from services.registro_meteorologico_service import RegistroMeteorologicoService
from exceptions.erros import RecursoNaoEncontradoError

class BackendServicesTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine('sqlite+pysqlite:///:memory:')
        base.Base.metadata.create_all(self.engine)
        self.session=Session(self.engine)
    def tearDown(self):
        self.session.close();self.engine.dispose()
    def test_missing_resource(self):
        with self.assertRaises(RecursoNaoEncontradoError):PontoObservacaoService(self.session).buscar_por_id(999)
    def test_optional_source_and_optional_city(self):
        p=PontoObservacaoService(self.session).criar({'nome':'Estação','latitude':'-22.9','longitude':'-43.2'})
        self.assertIsNone(p.cidade)
        f=FonteDadosService(self.session).criar({'nome':'INMET','tipo':'API'})
        self.assertIsNone(f.descricao)
    def test_future_and_precision(self):
        p=PontoObservacaoService(self.session).criar({'nome':'Estação','latitude':'-22.9','longitude':'-43.2'})
        f=FonteDadosService(self.session).criar({'nome':'INMET','tipo':'API'})
        data={'ponto_observacao_id':p.ponto_observacao_id,'fonte_dados_id':f.fonte_dados_id,
              'data_hora':'2099-01-01T10:00:00','temperatura':20,'umidade':60,'precipitacao':0}
        with self.assertRaises(ValueError):RegistroMeteorologicoService(self.session).criar(data)
        with self.assertRaises(ValueError):RegistroMeteorologicoService(self.session).criar({**data,'data_hora':'2026-10-10T10:00:00','temperatura':'22.229'})
