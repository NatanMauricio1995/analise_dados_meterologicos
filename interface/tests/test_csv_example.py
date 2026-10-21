import tempfile
import unittest
from pathlib import Path

from interface.services.csv_service import CSVImportService
from interface.services.storage import DataStore


class CSVExampleTests(unittest.TestCase):
    def test_example_csv_creates_points_sources_and_records(self):
        example = Path(__file__).resolve().parents[1] / "exemplos" / "observacoes_exemplo.csv"
        with tempfile.TemporaryDirectory() as temp:
            store = DataStore(temp)
            result = CSVImportService(store).import_file(example)
            self.assertEqual(result["importadas"], 4)
            self.assertEqual(result["rejeitadas"], 0)
            self.assertEqual(result["pontos_criados"], 2)
            self.assertEqual(result["fontes_criadas"], 2)
            self.assertEqual(len(store.list("pontos")), 2)
            self.assertEqual(len(store.list("fontes")), 2)
            self.assertEqual(len(store.list("registros")), 4)


if __name__ == "__main__":
    unittest.main()
