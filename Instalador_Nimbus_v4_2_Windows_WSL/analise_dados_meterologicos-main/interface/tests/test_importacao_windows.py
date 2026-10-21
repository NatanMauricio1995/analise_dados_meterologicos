"""Cenários que reproduziam a falha de importação em Windows sem tzdata."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfoNotFoundError

from interface.services.storage import DataStore
from shared.json_service import JSONImportService
from shared import validators

class WindowsJSONImportTests(unittest.TestCase):
    def test_windows_without_tzdata_imports_json(self):
        doc={'observacoes':[{
            'ponto':{'nome':'Ponto teste','latitude':-22.9,'longitude':-43.2},
            'fonte':{'nome':'Fonte teste','tipo':'Simulada'},
            'data_hora':'2026-10-13T11:00:00',
            'temperatura':25.0,'umidade':75,'precipitacao':0.0
        }]}
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'dados.json'
            path.write_text(json.dumps(doc),encoding='utf-8')
            store=DataStore(Path(d)/'persistencia')
            with patch.object(validators,'ZoneInfo',side_effect=ZoneInfoNotFoundError('tzdata absent')):
                first=JSONImportService(store).import_file(path)
                self.assertEqual((first['importadas'],first['rejeitadas']), (1,0))
                second=JSONImportService(store).import_file(path)
                self.assertEqual((second['duplicadas'], second['rejeitadas']), (1,0))
                self.assertEqual(second['linhas'][0]['status'], 'DUPLICADA')

    def test_multiple_bad_rows_report_reasons(self):
        with tempfile.TemporaryDirectory() as d:
            store=DataStore(d)
            result=JSONImportService(store).import_document({'observacoes':[42,{'ponto':{}}]})
            self.assertEqual(result['rejeitadas'],2)
            self.assertEqual(result['duplicadas'],0)
            self.assertEqual(result['importadas'],0)

if __name__=='__main__':unittest.main()
