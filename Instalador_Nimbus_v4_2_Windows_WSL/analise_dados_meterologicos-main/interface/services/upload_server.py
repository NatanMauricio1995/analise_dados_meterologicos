"""Recebe arquivos JSON do computador quando o Nimbus roda no Codespaces."""

import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

MAX_SIZE = 15 * 1024 * 1024


class BrowserJSONUploadServer:
    def __init__(self, upload_dir, host="0.0.0.0", port=8765):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.token = secrets.token_urlsafe(24)
        self.server = HTTPServer((host, port), self.handler())
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def handler(self):
        upload_dir = self.upload_dir
        interface_dir = upload_dir.parent.parent
        token = self.token

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def reply(self, code, content_type, body):
                self.send_response(code)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

            def error(self, code, message):
                body = json.dumps({"error": message}, ensure_ascii=False).encode("utf-8")
                self.reply(code, "application/json; charset=utf-8", body)

            def do_GET(self):
                route = urlparse(self.path).path
                if route == "/logo.png":
                    path = interface_dir / "recursos" / "nimbus_logo.png"
                    if path.exists():
                        self.reply(200, "image/png", path.read_bytes())
                    else:
                        self.error(404, "Logo não encontrada.")
                elif route == "/":
                    page = interface_dir / "recursos" / "upload.html"
                    html = page.read_text(encoding="utf-8").replace("__TOKEN__", token)
                    self.reply(200, "text/html; charset=utf-8", html.encode("utf-8"))
                else:
                    self.error(404, "Página não encontrada.")

            def do_POST(self):
                if urlparse(self.path).path != "/upload":
                    self.error(404, "Endereço não encontrado.")
                    return
                if self.headers.get("X-Nimbus-Token") != token:
                    self.error(403, "Envio não autorizado.")
                    return

                try:
                    size = int(self.headers.get("Content-Length", 0))
                except ValueError:
                    self.error(400, "Content-Length inválido.")
                    return
                if size <= 0 or size > MAX_SIZE:
                    self.error(400 if size <= 0 else 413, "Arquivo vazio ou maior que 15 MB.")
                    return

                name = parse_qs(urlparse(self.path).query).get("filename", ["dados.json"])[0]
                name = Path(name.replace("\\", "/")).name
                if Path(name).suffix.lower() != ".json":
                    self.error(415, "Selecione um arquivo JSON.")
                    return

                content = self.rfile.read(size)
                try:
                    content.decode("utf-8-sig")
                except UnicodeDecodeError:
                    self.error(400, "O JSON deve estar codificado em UTF-8.")
                    return

                try:
                    payload=json.loads(content.decode('utf-8-sig'))
                    if not isinstance(payload,dict) or not isinstance(payload.get('observacoes'),list):
                        raise ValueError('Documento deve conter observacoes como lista.')
                except (json.JSONDecodeError,ValueError) as exc:
                    self.error(400,f'Arquivo JSON inválido: {exc}')
                    return
                original = Path(name)
                destination = upload_dir / name
                number = 2
                while destination.exists():
                    destination = upload_dir / f"{original.stem}_{number}.json"
                    number += 1
                destination.write_bytes(content)
                body = json.dumps({"filename": destination.name}, ensure_ascii=False).encode("utf-8")
                self.reply(201, "application/json; charset=utf-8", body)

        return Handler

    def start(self):
        self.thread.start()
        return self

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
