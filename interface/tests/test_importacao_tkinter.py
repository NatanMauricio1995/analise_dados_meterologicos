"""Teste de regressão: botão de importação Tkinter deve permanecer referenciado.

O teste integra a GUI com o importador JSON real, sem Docker ou MySQL.
É executado quando o sistema permite criar uma janela Tk (Windows ou Xvfb).
"""
import json
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from interface.services.storage import DataStore
from interface.telas.importacao_json import JSONPage


class ImportacaoTkinterTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"Ambiente sem display para Tkinter: {exc}")
        self.root.withdraw()
        self.errors = []
        self.root.report_callback_exception = lambda *args: self.errors.append(args)
        self.temp = tempfile.TemporaryDirectory()
        self.store = DataStore(self.temp.name)
        self.page = JSONPage(self.root, self.store)
        self.page.pack()

    def tearDown(self):
        if hasattr(self, 'root'):
            self.root.destroy()
        if hasattr(self, 'temp'):
            self.temp.cleanup()

    def test_botao_importa_json_e_permanece_ativo(self):
        self.assertIsInstance(self.page.import_button, tk.Button)
        self.assertEqual(self.page.import_button['state'], 'normal')
        doc = {'observacoes': [{
            'ponto': {'nome': 'Estacao de Teste', 'latitude': -22.9, 'longitude': -43.2},
            'fonte': {'nome': 'Fonte simulada', 'tipo': 'Manual'},
            'data_hora': '2026-10-13T10:00:00',
            'temperatura': 25.0, 'umidade': 60.0, 'precipitacao': 0.5,
        }]}
        file = Path(self.temp.name) / 'entrada.json'
        file.write_text(json.dumps(doc), encoding='utf-8')
        self.page.set_selected_file(file)
        with patch('interface.telas.importacao_json.messagebox.showinfo'):
            self.page.import_button.invoke()
            self.assertEqual(len(self.store.list('registros')), 1)
            self.assertIn('Importadas: 1', self.page.summary['text'])
            self.assertEqual(self.page.import_button['state'], 'normal')
            self.page.import_button.invoke()
        self.assertEqual(len(self.store.list('registros')), 1)
        self.assertIn('Duplicadas: 1', self.page.summary['text'])
        self.assertEqual(len(self.page.report.get_children()), 1)
        self.assertEqual(self.errors, [])

    def test_erro_json_nao_trava_botao(self):
        self.assertIsInstance(self.page.import_button, tk.Button)
        file = Path(self.temp.name) / 'invalido.json'
        file.write_text('{json invalido}', encoding='utf-8')
        self.page.set_selected_file(file)
        with patch('interface.telas.importacao_json.messagebox.showerror') as err:
            self.page.import_button.invoke()
        err.assert_called_once()
        self.assertEqual(self.page.import_button['state'], 'normal')
        self.assertIn('Importação não concluída', self.page.summary['text'])
        self.assertEqual(self.errors, [])


if __name__ == '__main__':
    unittest.main()
