"""Salva os dados locais em arquivos JSON durante o desenvolvimento."""

import json
from pathlib import Path


FILES = {
    "pontos": "pontos_observacao.json",
    "fontes": "fontes_dados.json",
    "registros": "registros_meteorologicos.json",
}


class DataStore:
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or Path(__file__).resolve().parents[1] / "dados")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data = {name: self._load(name) for name in FILES}

    def _load(self, name):
        path = self.data_dir / FILES[name]
        old_path = self.data_dir.parent / FILES[name]
        if not path.exists() and old_path.exists():
            path = old_path
        if not path.exists():
            return []

        try:
            with path.open(encoding="utf-8") as file:
                rows = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(f"O arquivo {path.name} está com JSON inválido.") from exc

        if not isinstance(rows, list):
            raise ValueError(f"O arquivo {path.name} deve conter uma lista.")

        # Copia os arquivos antigos para a pasta dados, sem apagar o original.
        if path == old_path:
            self._write_file(self.data_dir / FILES[name], rows)
        return rows

    @staticmethod
    def _write_file(path, rows):
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(rows, file, ensure_ascii=False, indent=4)
        temporary.replace(path)

    def save_import(self, points, sources, records):
        """Grava o lote. Em erro, tenta restaurar estado e arquivos anteriores."""
        import copy
        old = copy.deepcopy(self.data)
        try:
            self.data['pontos'].extend(points)
            self.data['fontes'].extend(sources)
            start = self.next_id('registros')
            self.data['registros'].extend([{'id':start+i,**record} for i,record in enumerate(records)])
            for name in FILES:
                self._write(name)
        except OSError:
            self.data = old
            for name in FILES:
                self._write(name)
            raise

    def list(self, name):
        return self.data[name]

    def _write(self, name):
        self._write_file(self.data_dir / FILES[name], self.data[name])

    def next_id(self, name):
        return max((int(row["id"]) for row in self.data[name]), default=0) + 1

    def add(self, name, values):
        item = {"id": self.next_id(name), **values}
        self.data[name].append(item)
        try:
            self._write(name)
        except OSError:
            self.data[name].pop()
            raise
        return item

    def add_many(self, name, rows):
        if not rows:
            return []
        start_id = self.next_id(name)
        added = [{"id": start_id + i, **row} for i, row in enumerate(rows)]
        self.data[name].extend(added)
        try:
            self._write(name)
        except OSError:
            del self.data[name][-len(added):]
            raise
        return added

    def update(self, name, item_id, values):
        for index, row in enumerate(self.data[name]):
            if int(row["id"]) == int(item_id):
                old = row
                self.data[name][index] = {"id": int(item_id), **values}
                try:
                    self._write(name)
                except OSError:
                    self.data[name][index] = old
                    raise
                return self.data[name][index]
        raise KeyError("Registro não encontrado.")

    def delete(self, name, item_id):
        for index, row in enumerate(self.data[name]):
            if int(row["id"]) == int(item_id):
                removed = self.data[name].pop(index)
                try:
                    self._write(name)
                except OSError:
                    self.data[name].insert(index, removed)
                    raise
                return removed
        raise KeyError("Registro não encontrado.")
