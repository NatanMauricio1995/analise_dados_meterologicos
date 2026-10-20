"""Persistência local temporária em JSON para desenvolvimento do frontend.

Na versão integrada, a interface deverá consultar a API REST, que persistirá
os dados no MySQL. Este módulo não utiliza SQLite.
"""

import json
from pathlib import Path


class DataStore:
    FILES = {
        "pontos": "pontos_observacao.json",
        "fontes": "fontes_dados.json",
        "registros": "registros_meteorologicos.json",
    }

    def __init__(self, data_dir=None):
        base = Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / "dados"
        self.data_dir = base
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data = {key: self._load(key) for key in self.FILES}

    def _load(self, entity):
        path = self.data_dir / self.FILES[entity]
        source_path = path
        if not source_path.exists():
            # Migra automaticamente os JSON da versão anterior, que ficavam
            # diretamente na pasta interface/, para interface/dados/.
            legacy_path = self.data_dir.parent / self.FILES[entity]
            if legacy_path.exists():
                source_path = legacy_path
            else:
                return []
        try:
            with source_path.open("r", encoding="utf-8") as file:
                content = json.load(file)
            if not isinstance(content, list):
                raise ValueError(f"O arquivo {source_path.name} não contém uma lista JSON.")
            if source_path != path:
                with path.open("w", encoding="utf-8") as file:
                    json.dump(content, file, ensure_ascii=False, indent=4)
            return content
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"O arquivo {source_path.name} está corrompido. Faça uma cópia antes de corrigi-lo."
            ) from exc

    def list(self, entity):
        return self.data[entity]

    def _write(self, entity):
        path = self.data_dir / self.FILES[entity]
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(self.data[entity], file, ensure_ascii=False, indent=4)
        temporary.replace(path)

    def next_id(self, entity):
        return max((int(item.get("id", 0)) for item in self.data[entity]), default=0) + 1

    def add(self, entity, values):
        item = {"id": self.next_id(entity), **values}
        self.data[entity].append(item)
        try:
            self._write(entity)
        except OSError:
            self.data[entity].pop()
            raise
        return item

    def update(self, entity, item_id, values):
        index = next(
            (i for i, item in enumerate(self.data[entity]) if int(item["id"]) == int(item_id)),
            None,
        )
        if index is None:
            raise KeyError("Registro não encontrado.")
        previous = self.data[entity][index].copy()
        self.data[entity][index] = {"id": int(item_id), **values}
        try:
            self._write(entity)
        except OSError:
            self.data[entity][index] = previous
            raise
        return self.data[entity][index]

    def delete(self, entity, item_id):
        index = next(
            (i for i, item in enumerate(self.data[entity]) if int(item["id"]) == int(item_id)),
            None,
        )
        if index is None:
            raise KeyError("Registro não encontrado.")
        removed = self.data[entity].pop(index)
        try:
            self._write(entity)
        except OSError:
            self.data[entity].insert(index, removed)
            raise
        return removed

    def add_many(self, entity, rows):
        created = []
        next_id = self.next_id(entity)
        for offset, row in enumerate(rows):
            created.append({"id": next_id + offset, **row})
        self.data[entity].extend(created)
        try:
            self._write(entity)
        except OSError:
            del self.data[entity][-len(created):]
            raise
        return created
