"""Cliente HTTP para a futura integração com a API do backend."""

import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class APIClient:
    def __init__(self, address="http://127.0.0.1:5000"):
        self.address = address.rstrip("/")

    def request(self, method, route, data=None):
        body = None if data is None else json.dumps(data).encode("utf-8")
        request = Request(
            f"{self.address}/{route.lstrip('/')}",
            data=body,
            headers={"Content-Type": "application/json"},
            method=method.upper(),
        )
        try:
            with urlopen(request, timeout=8) as response:
                result = response.read().decode("utf-8")
                return json.loads(result) if result else None
        except HTTPError as exc:
            raise RuntimeError(f"Erro HTTP {exc.code}: {exc.reason}") from exc
        except URLError as exc:
            raise ConnectionError(f"Não foi possível conectar à API: {exc.reason}") from exc

    def get(self, route):
        return self.request("GET", route)

    def post(self, route, data):
        return self.request("POST", route, data)

    def put(self, route, data):
        return self.request("PUT", route, data)

    def delete(self, route):
        return self.request("DELETE", route)
