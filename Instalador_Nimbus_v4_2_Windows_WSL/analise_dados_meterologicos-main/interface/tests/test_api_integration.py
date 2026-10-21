"""API Flask SQLite: requer Flask instalado e URL de banco de teste."""
import os,sys,unittest
from pathlib import Path
try:
    import flask
except ImportError:
    flask=None

@unittest.skipUnless(flask is not None,'Flask indisponível neste ambiente')
class ApiIntegrationTests(unittest.TestCase):
    def setUp(self):
        os.environ['NIMBUS_DATABASE_URL']='sqlite+pysqlite:///:memory:'
        sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'projeto_API'))
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from entities.base import Base
        from entities import ponto_observacao,fonte_dados,registro_meteorologico  # noqa
        from app import create_app
        self.engine=create_engine('sqlite+pysqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.client=create_app(sessionmaker(bind=self.engine)).test_client()
    def tearDown(self):self.engine.dispose()
    def test_rest_error_codes_and_json_import(self):
        self.assertEqual(self.client.get('/api/pontos-observacao/123').status_code,404)
        src=self.client.post('/api/fontes-dados',json={'nome':'INMET','tipo':'API'})
        self.assertEqual(src.status_code,201)
        bad=self.client.post('/api/registros',json={'umidade':121})
        self.assertEqual(bad.status_code,400)
        doc={'observacoes':[{'ponto':{'nome':'A','latitude':-22,'longitude':-43},'fonte':{'nome':'INMET','tipo':'API'},'data_hora':'2026-10-10T10:00:00','temperatura':20,'umidade':70,'precipitacao':1.2}]}
        res=self.client.post('/api/importacoes/json',json=doc)
        self.assertEqual(res.status_code,200,res.json)
        self.assertEqual(res.json['importadas'],1)
        self.assertEqual(self.client.get('/api/registros').status_code,200)
