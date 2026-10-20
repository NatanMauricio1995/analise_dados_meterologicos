"""Servidor mínimo para receber CSVs do computador do usuário no Codespaces.

A página HTML abre no navegador local e usa <input type=file>, permitindo
selecionar um arquivo do PC e enviá-lo ao Codespace pela porta encaminhada.
O servidor deve ser exposto somente por uma porta Private do Codespaces.
"""

from __future__ import annotations

import json
import re
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15 MB


class BrowserCSVUploadServer:
    def __init__(self, upload_dir: Path | str, host: str = "0.0.0.0", port: int = 8765):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.token = secrets.token_urlsafe(24)
        self._httpd = ThreadingHTTPServer((host, port), self._make_handler())
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(
            target=self._httpd.serve_forever,
            name="nimbus-csv-upload",
            daemon=True,
        )

    def _make_handler(self):
        upload_dir = self.upload_dir
        token = self.token

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                return

            def _send(self, status: int, content_type: str, body: bytes):
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                route = urlparse(self.path).path
                if route == "/health":
                    self._send(200, "application/json; charset=utf-8", b'{"status":"ok"}')
                    return
                if route != "/":
                    self._send(404, "text/plain; charset=utf-8", "Página não encontrada.".encode())
                    return

                html = HTML_PAGE.replace("__NIMBUS_UPLOAD_TOKEN__", token).encode("utf-8")
                self._send(200, "text/html; charset=utf-8", html)

            def do_POST(self):
                if urlparse(self.path).path != "/upload":
                    self._send(404, "application/json; charset=utf-8", b'{"error":"Rota nao encontrada."}')
                    return

                if self.headers.get("X-Nimbus-Token", "") != token:
                    self._send(403, "application/json; charset=utf-8", b'{"error":"Envio nao autorizado."}')
                    return

                try:
                    length = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    length = 0

                if length <= 0:
                    self._send(400, "application/json; charset=utf-8", b'{"error":"Arquivo vazio."}')
                    return
                if length > MAX_UPLOAD_BYTES:
                    self._send(413, "application/json; charset=utf-8", b'{"error":"O arquivo excede 15 MB."}')
                    return

                query = parse_qs(urlparse(self.path).query)
                original_name = query.get("filename", ["observacoes.csv"])[0]
                safe_basename = Path(original_name.replace("\\", "/")).name
                if Path(safe_basename).suffix.lower() != ".csv":
                    self._send(415, "application/json; charset=utf-8", b'{"error":"Selecione um arquivo .csv."}')
                    return

                stem = Path(safe_basename).stem
                stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._") or "observacoes"
                filename = f"{stem}.csv"
                destination = upload_dir / filename
                counter = 2
                while destination.exists():
                    filename = f"{stem}_{counter}.csv"
                    destination = upload_dir / filename
                    counter += 1

                content = self.rfile.read(length)
                if not content:
                    self._send(400, "application/json; charset=utf-8", b'{"error":"Arquivo vazio."}')
                    return

                try:
                    # Recusa arquivos binários e textos que não sejam UTF-8.
                    content.decode("utf-8-sig")
                    destination.write_bytes(content)
                except UnicodeDecodeError:
                    self._send(400, "application/json; charset=utf-8", b'{"error":"O CSV deve estar codificado em UTF-8."}')
                    return
                except OSError:
                    self._send(500, "application/json; charset=utf-8", b'{"error":"Nao foi possivel salvar o arquivo."}')
                    return

                response = json.dumps(
                    {"filename": filename, "message": "Arquivo enviado ao Nimbus com sucesso."},
                    ensure_ascii=False,
                ).encode("utf-8")
                self._send(201, "application/json; charset=utf-8", response)

        return Handler

    def start(self):
        self._thread.start()
        return self

    def stop(self):
        if self._thread.is_alive():
            self._httpd.shutdown()
            self._httpd.server_close()


HTML_PAGE = r'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nimbus | Enviar CSV</title>
<style>
:root{font-family:Arial,sans-serif;color:#171717;background:#f4f5f7}
*{box-sizing:border-box}body{margin:0;padding:32px 16px}
main{max-width:620px;margin:30px auto;background:white;border:1px solid #e5e7eb;border-radius:14px;padding:28px;box-shadow:0 8px 28px #1111110c}
h1{margin:0 0 8px;font-size:26px}p{color:#6b7280;line-height:1.55}
.drop{margin:22px 0;padding:25px;border:2px dashed #cbd5e1;border-radius:10px;background:#f9fafb;text-align:center}
input{display:block;width:100%;margin:14px 0;font-size:14px}
button{background:#171717;color:white;border:0;border-radius:7px;padding:12px 20px;font-weight:bold;cursor:pointer}
button:disabled{opacity:.45;cursor:not-allowed}.name{font-size:13px;color:#475569;overflow-wrap:anywhere}
#status{margin-top:18px;padding:12px;border-radius:8px;display:none;white-space:pre-wrap}
.ok{display:block!important;background:#ecfdf5;color:#166534}.err{display:block!important;background:#fef2f2;color:#b91c1c}
.note{font-size:12px;border-top:1px solid #e5e7eb;margin-top:22px;padding-top:14px}
</style>
</head>
<body>
<main>
<h1>Nimbus — Enviar arquivo CSV</h1>
<p>Escolha um arquivo CSV salvo neste computador. Depois do envio, volte ao Nimbus e atualize a lista de arquivos recebidos.</p>
<div class="drop">
<strong>Selecione o arquivo no seu computador</strong>
<input id="file" type="file" accept=".csv,text/csv">
<div id="name" class="name">Nenhum arquivo selecionado.</div>
</div>
<button id="send" disabled>Enviar CSV para o Nimbus</button>
<div id="status"></div>
<p class="note">Formato esperado: UTF-8, separador ponto e vírgula (;), ponto como separador decimal e cabeçalho do Nimbus. Tamanho máximo: 15 MB. Mantenha esta porta como Private no Codespaces.</p>
</main>
<script>
const token = "__NIMBUS_UPLOAD_TOKEN__";
const input = document.getElementById("file");
const send = document.getElementById("send");
const name = document.getElementById("name");
const statusBox = document.getElementById("status");
input.addEventListener("change", () => {
  const file = input.files && input.files[0];
  name.textContent = file ? `${file.name} (${(file.size/1024).toFixed(1)} KB)` : "Nenhum arquivo selecionado.";
  send.disabled = !file;
  statusBox.className = "";
  statusBox.style.display = "none";
});
send.addEventListener("click", async () => {
  const file = input.files && input.files[0];
  if (!file) return;
  send.disabled = true;
  send.textContent = "Enviando...";
  statusBox.className = "";
  statusBox.style.display = "none";
  try {
    const response = await fetch("/upload?filename=" + encodeURIComponent(file.name), {
      method: "POST",
      headers: {"Content-Type":"application/octet-stream", "X-Nimbus-Token":token},
      body: file
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Falha no envio.");
    statusBox.textContent = `Arquivo recebido: ${result.filename}\nVolte ao Nimbus e clique em “Atualizar arquivos recebidos”.`;
    statusBox.className = "ok";
  } catch (error) {
    statusBox.textContent = error.message || "Não foi possível enviar o arquivo.";
    statusBox.className = "err";
  } finally {
    send.disabled = false;
    send.textContent = "Enviar CSV para o Nimbus";
  }
});
</script>
</body>
</html>'''
