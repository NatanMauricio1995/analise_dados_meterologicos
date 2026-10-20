import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from interface.services.upload_server import BrowserCSVUploadServer


class BrowserCSVUploadServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        interface_dir = root / "interface"
        resources = interface_dir / "recursos"
        upload_dir = interface_dir / "dados" / "importacoes"
        resources.mkdir(parents=True)
        upload_dir.mkdir(parents=True)
        self.upload_dir = upload_dir
        (resources / "nimbus_logo.png").write_bytes(b"fake-png-for-route-test")
        self.server = BrowserCSVUploadServer(upload_dir, host="127.0.0.1", port=0)
        self.server.start()
        self.base_url = f"http://127.0.0.1:{self.server.port}"

    def tearDown(self):
        self.server.stop()
        self.temp.cleanup()

    def test_upload_page_has_local_file_picker(self):
        with urlopen(self.base_url + "/") as response:
            html = response.read().decode("utf-8")
        self.assertIn('type="file"', html)
        self.assertIn('accept=".csv,text/csv"', html)
        self.assertIn('src="/logo.png"', html)
        self.assertIn("Enviar arquivo CSV", html)

    def test_upload_page_serves_nimbus_logo(self):
        with urlopen(self.base_url + "/logo.png") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get_content_type(), "image/png")
            self.assertEqual(response.read(), b"fake-png-for-route-test")

    def test_upload_csv_saves_file(self):
        content = (
            "ponto_observacao_id;fonte_dados_id;data_hora;temperatura;umidade;precipitacao\n"
            "1;1;2026-10-10 14:00:00;23.5;72;0.0\n"
        ).encode("utf-8")
        request = Request(
            self.base_url + "/upload?filename=teste_nimbus.csv",
            data=content,
            headers={
                "Content-Type": "application/octet-stream",
                "X-Nimbus-Token": self.server.token,
            },
            method="POST",
        )
        with urlopen(request) as response:
            result = json.loads(response.read().decode("utf-8"))
            self.assertEqual(response.status, 201)
        self.assertEqual(result["filename"], "teste_nimbus.csv")
        self.assertEqual(
            (self.upload_dir / "teste_nimbus.csv").read_bytes(),
            content,
        )

    def test_upload_rejects_wrong_token(self):
        request = Request(
            self.base_url + "/upload?filename=teste.csv",
            data=b"a;b\n1;2\n",
            headers={
                "Content-Type": "application/octet-stream",
                "X-Nimbus-Token": "invalid-token",
            },
            method="POST",
        )
        with self.assertRaises(HTTPError) as context:
            urlopen(request)
        self.assertEqual(context.exception.code, 403)

    def test_upload_rejects_non_csv(self):
        request = Request(
            self.base_url + "/upload?filename=teste.txt",
            data=b"conteudo",
            headers={
                "Content-Type": "application/octet-stream",
                "X-Nimbus-Token": self.server.token,
            },
            method="POST",
        )
        with self.assertRaises(HTTPError) as context:
            urlopen(request)
        self.assertEqual(context.exception.code, 415)


if __name__ == "__main__":
    unittest.main()
