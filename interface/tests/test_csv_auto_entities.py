import tempfile
import unittest
from pathlib import Path

from interface.services.storage import DataStore
from interface.services.csv_service import CSVImportService, HEADERS


class CSVAutoEntityImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = DataStore(self.temp.name)
        self.csv_path = Path(self.temp.name) / "observacoes_com_cadastros.csv"

    def tearDown(self):
        self.temp.cleanup()

    def write_csv(self, rows):
        content = ";".join(HEADERS) + "\n"
        content += "\n".join(";".join(row) for row in rows) + "\n"
        self.csv_path.write_text(content, encoding="utf-8")

    def test_import_creates_points_sources_and_records_automatically(self):
        self.write_csv([
            ["ESTACAO CENTRAL", "-22.9035", "-43.2096", "RIO DE JANEIRO", "RJ",
             "INMET", "API", "FONTE OFICIAL", "2026-10-18 08:00:00", "23.5", "72", "0.0"],
            ["ESTACAO CENTRAL", "-22.9035", "-43.2096", "RIO DE JANEIRO", "RJ",
             "INMET", "API", "FONTE OFICIAL", "2026-10-18 14:00:00", "29.8", "61", "0.0"],
            ["ESTACAO SERRANA", "-22.4610", "-42.6530", "TERESOPOLIS", "RJ",
             "OPEN-METEO", "API", "SERVICO METEOROLOGICO", "2026-10-18 08:00:00", "18.6", "86", "2.4"],
        ])

        result = CSVImportService(self.store).import_file(self.csv_path)

        self.assertEqual(result["importadas"], 3)
        self.assertEqual(result["rejeitadas"], 0)
        self.assertEqual(result["pontos_criados"], 2)
        self.assertEqual(result["fontes_criadas"], 2)
        self.assertEqual(len(self.store.list("pontos")), 2)
        self.assertEqual(len(self.store.list("fontes")), 2)
        self.assertEqual(len(self.store.list("registros")), 3)

    def test_import_reuses_existing_point_and_source(self):
        point = self.store.add("pontos", {
            "nome": "ESTACAO CENTRAL", "latitude": "-22.903500",
            "longitude": "-43.209600", "cidade": "RIO DE JANEIRO", "estado": "RJ",
        })
        source = self.store.add("fontes", {
            "nome": "INMET", "tipo": "API", "descricao": "FONTE OFICIAL",
        })
        self.write_csv([
            ["ESTACAO CENTRAL", "-22.9035", "-43.2096", "RIO DE JANEIRO", "RJ",
             "INMET", "API", "OUTRA DESCRICAO", "2026-10-18 08:00:00", "23.5", "72", "0.0"],
        ])

        result = CSVImportService(self.store).import_file(self.csv_path)

        self.assertEqual(result["importadas"], 1)
        self.assertEqual(result["pontos_criados"], 0)
        self.assertEqual(result["fontes_criadas"], 0)
        record = self.store.list("registros")[0]
        self.assertEqual(record["ponto_observacao_id"], point["id"])
        self.assertEqual(record["fonte_dados_id"], source["id"])

    def test_invalid_observation_does_not_create_orphan_point_or_source(self):
        self.write_csv([
            ["PONTO INVALIDO", "-22.9", "-43.2", "CIDADE", "RJ",
             "FONTE INVALIDA", "API", "DESC", "2026-10-18 08:00:00", "23.5", "150", "0.0"],
        ])

        result = CSVImportService(self.store).import_file(self.csv_path)

        self.assertEqual(result["importadas"], 0)
        self.assertEqual(result["rejeitadas"], 1)
        self.assertEqual(result["pontos_criados"], 0)
        self.assertEqual(result["fontes_criadas"], 0)
        self.assertEqual(len(self.store.list("pontos")), 0)
        self.assertEqual(len(self.store.list("fontes")), 0)

    def test_duplicate_rows_are_rejected_without_duplicate_entities(self):
        row = ["PONTO", "-22.9", "-43.2", "CIDADE", "RJ",
               "FONTE", "API", "DESC", "2026-10-18 08:00:00", "23.5", "72", "0.0"]
        self.write_csv([row, row])

        result = CSVImportService(self.store).import_file(self.csv_path)

        self.assertEqual(result["importadas"], 1)
        self.assertEqual(result["rejeitadas"], 1)
        self.assertEqual(result["pontos_criados"], 1)
        self.assertEqual(result["fontes_criadas"], 1)
        self.assertEqual(len(self.store.list("pontos")), 1)
        self.assertEqual(len(self.store.list("fontes")), 1)
        self.assertEqual(len(self.store.list("registros")), 1)

    def test_old_csv_format_with_ids_is_not_accepted(self):
        self.csv_path.write_text(
            "ponto_observacao_id;fonte_dados_id;data_hora;temperatura;umidade;precipitacao\n"
            "1;1;2026-10-18 08:00:00;23.5;72;0.0\n",
            encoding="utf-8",
        )
        with self.assertRaises(ValueError):
            CSVImportService(self.store).import_file(self.csv_path)

    def test_invalid_row_does_not_leave_wrong_ids_for_later_valid_rows(self):
        self.write_csv([
            ["PONTO INVALIDO", "91", "-43.2", "CIDADE", "RJ", "FONTE A", "API", "DESC",
             "2026-10-18 08:00:00", "23.5", "72", "0.0"],
            ["PONTO VALIDO", "-22.9", "-43.2", "CIDADE", "RJ", "FONTE B", "API", "DESC",
             "2026-10-18 09:00:00", "24.5", "70", "0.0"],
        ])
        result = CSVImportService(self.store).import_file(self.csv_path)
        self.assertEqual(result["importadas"], 1)
        self.assertEqual(result["rejeitadas"], 1)
        point = self.store.list("pontos")[0]
        source = self.store.list("fontes")[0]
        record = self.store.list("registros")[0]
        self.assertEqual(record["ponto_observacao_id"], point["id"])
        self.assertEqual(record["fonte_dados_id"], source["id"])


if __name__ == "__main__":
    unittest.main()
