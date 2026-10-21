import tempfile
import unittest
from pathlib import Path

from interface.services.storage import DataStore
from interface.services.validators import (
    ValidationError,
    validate_point,
    validate_source,
    validate_record,
)
from interface.services.csv_service import CSVImportService
from interface.services.statistics import filter_records, summarize, parse_date_range


class NimbusServicesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = DataStore(self.temp.name)
        self.point = self.store.add("pontos", validate_point({
            "nome": "Estação Centro",
            "latitude": "-22.90",
            "longitude": "-43.20",
            "cidade": "Rio de Janeiro",
            "estado": "rj",
        }))
        self.source = self.store.add("fontes", validate_source({
            "nome": "INMET", "tipo": "API", "descricao": ""
        }))

    def tearDown(self):
        self.temp.cleanup()

    def test_point_is_normalized_and_coordinates_are_checked(self):
        self.assertEqual(self.point["nome"], "ESTAÇÃO CENTRO")
        self.assertEqual(self.point["estado"], "RJ")
        with self.assertRaises(ValidationError):
            validate_point({
                "nome": "PONTO", "latitude": "91", "longitude": "0",
                "cidade": "CIDADE", "estado": "RJ"
            })

    def test_record_limits(self):
        with self.assertRaises(ValidationError):
            validate_record({
                "ponto_observacao_id": self.point["id"],
                "fonte_dados_id": self.source["id"],
                "data_hora": "2026-10-10 14:00:00",
                "temperatura": "23", "umidade": "101", "precipitacao": "0"
            }, {self.point["id"]}, {self.source["id"]})

    def test_csv_import_accepts_valid_and_reports_invalid_lines(self):
        csv_path = Path(self.temp.name) / "amostra.csv"
        header = (
            "ponto_nome;latitude;longitude;cidade;estado;fonte_nome;"
            "fonte_tipo;fonte_descricao;data_hora;temperatura;umidade;precipitacao\n"
        )
        point = "ESTAÇÃO CENTRO;-22.900000;-43.200000;RIO DE JANEIRO;RJ;"
        source = "INMET;API;FONTE OFICIAL;"
        rows = [
            point + source + "2026-10-10 14:00:00;23.5;72;0.0",
            point + source + "2026-10-10 14:00:00;23.5;72;0.0",  # duplicado
            point + source + "2026-10-10 15:00:00;23.5;120;0.0",  # umidade inválida
            ";-22.9;-43.2;RIO DE JANEIRO;RJ;INMET;API;FONTE;2026-10-10 16:00:00;20;60;0",
        ]
        csv_path.write_text(header + "\n".join(rows), encoding="utf-8")

        result = CSVImportService(self.store).import_file(csv_path)
        self.assertEqual(result["importadas"], 1)
        self.assertEqual(result["rejeitadas"], 3)
        self.assertEqual(len(self.store.list("pontos")), 1)
        self.assertEqual(len(self.store.list("fontes")), 1)
        self.assertEqual(len(self.store.list("registros")), 1)

    def test_statistics_and_date_filter(self):
        record = validate_record({
            "ponto_observacao_id": self.point["id"],
            "fonte_dados_id": self.source["id"],
            "data_hora": "2026-10-10 14:00:00",
            "temperatura": "23.5", "umidade": "72", "precipitacao": "0.5"
        }, {self.point["id"]}, {self.source["id"]})
        self.store.add("registros", record)
        start, end = parse_date_range("09-10-2026", "11-10-2026")
        filtered = filter_records(self.store.list("registros"), self.point["id"], start, end)
        stats = summarize(filtered)
        self.assertEqual(stats["quantidade"], 1)
        self.assertAlmostEqual(stats["temperatura_media"], 23.5)

    def test_storage_persists_between_instances(self):
        reloaded = DataStore(self.temp.name)
        self.assertEqual(len(reloaded.list("pontos")), 1)
        self.assertEqual(reloaded.list("pontos")[0]["estado"], "RJ")


if __name__ == "__main__":
    unittest.main()
