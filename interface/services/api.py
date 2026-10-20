"""Cliente HTTP preparado para a futura integração com a API Flask.

A interface ainda usa JSON local enquanto os endpoints do backend não estão
alinhados. Quando a API estiver disponível, as telas poderão substituir o
DataStore por este cliente sem acessar o MySQL diretamente.
"""

import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class APIClient:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip("/")

    def request(self, method, endpoint, data=None):
        body = None if data is None else json.dumps(data).encode("utf-8")
        request = Request(
            f"{self.base_url}/{endpoint.lstrip('/')}",
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method=method.upper(),
        )
        try:
            with urlopen(request, timeout=8) as response:
                content = response.read().decode("utf-8")
                return json.loads(content) if content else None
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API retornou HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise ConnectionError(f"Não foi possível conectar à API: {exc.reason}") from exc

    def get(self, endpoint):
        return self.request("GET", endpoint)

    def post(self, endpoint, data):
        return self.request("POST", endpoint, data)

    def put(self, endpoint, data):
        return self.request("PUT", endpoint, data)

    def delete(self, endpoint):
        return self.request("DELETE", endpoint)
