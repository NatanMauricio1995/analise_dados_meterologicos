import json
import tempfile
import unittest
from pathlib import Path

from interface.services.storage import DataStore
from interface.services.validators import ValidationError, validate_point, validate_source, validate_record
from interface.services.json_service import JSONImportService
from interface.services.statistics import filter_records, summarize, parse_date_range

POINT = {"nome":"Estação Centro","latitude":"-22.900000","longitude":"-43.200000","cidade":"Rio de Janeiro","estado":"RJ"}
SOURCE = {"nome":"INMET","tipo":"API"}

def row(**changes):
    r={"ponto":dict(POINT),"fonte":dict(SOURCE),"data_hora":"2026-10-10T14:00:00",
       "temperatura":23.5,"umidade":72,"precipitacao":0.5}
    return {**r,**changes}

class NimbusServicesTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=DataStore(self.temp.name)
        self.p=self.store.add('pontos',validate_point(POINT))
        self.s=self.store.add('fontes',validate_source(SOURCE))
    def tearDown(self):self.temp.cleanup()

    def test_point_and_optional_fields(self):
        self.assertEqual(self.p['estado'],'RJ')
        minimal=validate_point({'nome':'Sem cidade','latitude':-10,'longitude':-20})
        self.assertIsNone(minimal['cidade'])
        self.assertIsNone(minimal['estado'])
        with self.assertRaises(ValidationError):validate_point({**POINT,'estado':'XX'})
        with self.assertRaises(ValidationError):validate_point({**POINT,'latitude':-91})
        with self.assertRaises(ValidationError):validate_point({**POINT,'latitude':'-22.1234567'})
        with self.assertRaises(ValidationError):validate_point({**POINT,'nome':'x'*101})
    def test_source_optional_and_lengths(self):
        self.assertIsNone(validate_source(SOURCE)['descricao'])
        with self.assertRaises(ValidationError):validate_source({**SOURCE,'nome':'x'*120})
    def test_record_limits_no_implicit_rounding_or_future(self):
        values={'ponto_observacao_id':self.p['id'],'fonte_dados_id':self.s['id'],
                'data_hora':'2026-10-10T14:00:00','temperatura':23.5,'umidade':72,'precipitacao':0.5}
        self.assertEqual(validate_record(values,{self.p['id']},{self.s['id']})['temperatura'],'23.50')
        for changes in ({'temperatura':'22.229'},{'umidade':120},{'precipitacao':1000000},
                        {'data_hora':'2099-01-01T00:00:00'}):
            with self.subTest(changes=changes),self.assertRaises(ValidationError):
                validate_record({**values,**changes},{self.p['id']},{self.s['id']})
    def test_json_import_reports_per_item_and_creates_no_ghost_entities(self):
        p2={**POINT,'nome':'Nova estação'}
        rows=[row(),row(),row(umidade=140),row(ponto=p2,temperatura=200)]
        result=JSONImportService(self.store).import_document({'observacoes':rows})
        self.assertEqual((result['importadas'],result['rejeitadas'],result['duplicadas']),(1,2,1))
        self.assertEqual(len(self.store.list('pontos')),1)
        self.assertEqual(len(self.store.list('fontes')),1)
        self.assertEqual(len(self.store.list('registros')),1)
    def test_json_file_and_reuse_new_point(self):
        rows=[row(ponto={**POINT,'nome':'Estação Nova'}), row(ponto={**POINT,'nome':'Estação Nova'}, data_hora='2026-10-10T15:00:00')]
        path=Path(self.temp.name)/'input.json'
        path.write_text(json.dumps({'observacoes':rows}),encoding='utf8')
        res=JSONImportService(self.store).import_file(path)
        self.assertEqual((res['importadas'],res['pontos_criados']),(2,1))
        self.assertEqual(len(self.store.list('registros')),2)
        reloaded=DataStore(self.temp.name)
        self.assertEqual(len(reloaded.list('pontos')),2)
    def test_bad_document(self):
        for obj in ([],{}, {'observacoes':{}}, {'observacoes':["x"]}):
            if isinstance(obj,dict) and isinstance(obj.get('observacoes'),list):
                result=JSONImportService(self.store).import_document(obj)
                self.assertEqual(result['rejeitadas'],1)
            else:
                with self.assertRaises(ValueError):JSONImportService(self.store).import_document(obj)
    def test_statistics_source_and_point_are_not_summed_together(self):
        data=[validate_record({'ponto_observacao_id':self.p['id'],'fonte_dados_id':self.s['id'],
                 'data_hora':'2026-10-10T14:00:00','temperatura':22,'umidade':60,'precipitacao':11.2},
                 {self.p['id']},{self.s['id']})]
        alternative={**data[0],'fonte_dados_id':2,'precipitacao':'10.30'}
        totals=summarize([*data,alternative])
        self.assertIsNone(totals['precipitacao_total'])
        start,end=parse_date_range('09-10-2026','11-10-2026')
        self.assertEqual(summarize(filter_records([*data,alternative],self.p['id'],start,end,self.s['id']))['precipitacao_total'],11.2)
    def test_json_storage_persists(self):
        self.assertEqual(DataStore(self.temp.name).list('pontos')[0]['nome'],'ESTAÇÃO CENTRO')
