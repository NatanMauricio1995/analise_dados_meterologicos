"""Importação CSV que cria/reutiliza pontos e fontes automaticamente."""

import csv
from pathlib import Path

from .validators import (
    ValidationError,
    validate_point,
    validate_source,
    validate_record,
)

# Formato recomendado: cada linha descreve a observação e os dados do ponto/fonte.
EXTENDED_HEADERS = [
    "ponto_nome",
    "latitude",
    "longitude",
    "cidade",
    "estado",
    "fonte_nome",
    "fonte_tipo",
    "fonte_descricao",
    "data_hora",
    "temperatura",
    "umidade",
    "precipitacao",
]

# Compatibilidade retroativa com os CSVs antigos que utilizavam IDs já cadastrados.
LEGACY_HEADERS = [
    "ponto_observacao_id",
    "fonte_dados_id",
    "data_hora",
    "temperatura",
    "umidade",
    "precipitacao",
]


class CSVImportService:
    def __init__(self, store):
        self.store = store

    @staticmethod
    def _point_key(point):
        return (
            str(point["nome"]).strip().upper(),
            f"{float(point['latitude']):.6f}",
            f"{float(point['longitude']):.6f}",
            str(point["cidade"]).strip().upper(),
            str(point["estado"]).strip().upper(),
        )

    @staticmethod
    def _source_key(source):
        return (
            str(source["nome"]).strip().upper(),
            str(source["tipo"]).strip().upper(),
        )

    def _import_legacy(self, reader, current_records):
        points = self.store.list("pontos")
        sources = self.store.list("fontes")
        point_ids = {int(item["id"]) for item in points}
        source_ids = {int(item["id"]) for item in sources}
        seen_keys = {
            (
                int(item["ponto_observacao_id"]),
                int(item["fonte_dados_id"]),
                item["data_hora"],
            )
            for item in current_records
        }
        accepted = []
        lines = []

        for line_number, row in enumerate(reader, start=2):
            try:
                if None in row and row[None]:
                    raise ValidationError("A linha possui mais colunas do que o cabeçalho CSV.")
                values = {
                    str(key).strip(): str(value or "").strip()
                    for key, value in row.items()
                    if key is not None
                }
                normalized = validate_record(values, point_ids, source_ids)
                key = (
                    normalized["ponto_observacao_id"],
                    normalized["fonte_dados_id"],
                    normalized["data_hora"],
                )
                if key in seen_keys:
                    raise ValidationError("Registro duplicado para a mesma fonte, ponto e data/hora.")
                seen_keys.add(key)
                accepted.append(normalized)
                lines.append({"linha": line_number, "status": "IMPORTADA", "motivo": "Registro validado."})
            except (ValidationError, TypeError, ValueError) as exc:
                lines.append({"linha": line_number, "status": "REJEITADA", "motivo": str(exc)})

        if accepted:
            self.store.add_many("registros", accepted)

        return self._result(lines, created_points=0, created_sources=0)

    def _import_extended(self, reader, current_records):
        existing_points = self.store.list("pontos")
        existing_sources = self.store.list("fontes")

        point_by_key = {self._point_key(item): int(item["id"]) for item in existing_points}
        source_by_key = {self._source_key(item): int(item["id"]) for item in existing_sources}

        next_point_id = self.store.next_id("pontos")
        next_source_id = self.store.next_id("fontes")

        planned_points = {}
        planned_sources = {}
        accepted = []
        lines = []

        seen_keys = {
            (
                int(item["ponto_observacao_id"]),
                int(item["fonte_dados_id"]),
                item["data_hora"],
            )
            for item in current_records
        }

        used_point_ids = set()
        used_source_ids = set()

        for line_number, row in enumerate(reader, start=2):
            try:
                if None in row and row[None]:
                    raise ValidationError("A linha possui mais colunas do que o cabeçalho CSV.")

                values = {
                    str(key).strip(): str(value or "").strip()
                    for key, value in row.items()
                    if key is not None
                }

                point_values = validate_point({
                    "nome": values.get("ponto_nome", ""),
                    "latitude": values.get("latitude", ""),
                    "longitude": values.get("longitude", ""),
                    "cidade": values.get("cidade", ""),
                    "estado": values.get("estado", ""),
                })
                source_values = validate_source({
                    "nome": values.get("fonte_nome", ""),
                    "tipo": values.get("fonte_tipo", ""),
                    "descricao": values.get("fonte_descricao", ""),
                })

                point_key = self._point_key(point_values)
                source_key = self._source_key(source_values)

                point_id = point_by_key.get(point_key)
                if point_id is None:
                    point_id = next_point_id
                    next_point_id += 1
                    point_by_key[point_key] = point_id
                    planned_points[point_id] = point_values

                source_id = source_by_key.get(source_key)
                if source_id is None:
                    source_id = next_source_id
                    next_source_id += 1
                    source_by_key[source_key] = source_id
                    planned_sources[source_id] = source_values

                record_values = {
                    "ponto_observacao_id": str(point_id),
                    "fonte_dados_id": str(source_id),
                    "data_hora": values.get("data_hora", ""),
                    "temperatura": values.get("temperatura", ""),
                    "umidade": values.get("umidade", ""),
                    "precipitacao": values.get("precipitacao", ""),
                }
                normalized = validate_record(
                    record_values,
                    set(point_by_key.values()),
                    set(source_by_key.values()),
                )

                duplicate_key = (
                    normalized["ponto_observacao_id"],
                    normalized["fonte_dados_id"],
                    normalized["data_hora"],
                )
                if duplicate_key in seen_keys:
                    raise ValidationError("Registro duplicado para a mesma fonte, ponto e data/hora.")

                seen_keys.add(duplicate_key)
                used_point_ids.add(point_id)
                used_source_ids.add(source_id)
                accepted.append(normalized)
                lines.append({
                    "linha": line_number,
                    "status": "IMPORTADA",
                    "motivo": "Observação validada; ponto e fonte associados automaticamente.",
                })

            except (ValidationError, TypeError, ValueError) as exc:
                lines.append({"linha": line_number, "status": "REJEITADA", "motivo": str(exc)})

        # Evita criar pontos/fontes sem nenhuma observação válida associada.
        new_points = [value for item_id, value in planned_points.items() if item_id in used_point_ids]
        new_sources = [value for item_id, value in planned_sources.items() if item_id in used_source_ids]

        # Persiste as três entidades como uma única operação lógica; tenta restaurar
        # os dados anteriores se qualquer gravação falhar.
        snapshots = {
            entity: [dict(item) for item in self.store.list(entity)]
            for entity in ("pontos", "fontes", "registros")
        }
        try:
            if new_points:
                self.store.add_many("pontos", new_points)
            if new_sources:
                self.store.add_many("fontes", new_sources)
            if accepted:
                self.store.add_many("registros", accepted)
        except Exception as exc:
            for entity, snapshot in snapshots.items():
                self.store.list(entity)[:] = snapshot
            for entity in snapshots:
                try:
                    self.store._write(entity)
                except Exception:
                    pass
            raise ValueError(
                "Não foi possível salvar a importação. Nenhuma alteração foi mantida. "
                f"Detalhe: {exc}"
            ) from exc

        return self._result(
            lines,
            created_points=len(new_points),
            created_sources=len(new_sources),
        )

    @staticmethod
    def _result(lines, created_points, created_sources):
        return {
            "importadas": sum(1 for row in lines if row["status"] == "IMPORTADA"),
            "rejeitadas": sum(1 for row in lines if row["status"] == "REJEITADA"),
            "pontos_criados": created_points,
            "fontes_criadas": created_sources,
            "linhas": lines,
        }

    def import_file(self, filename):
        path = Path(filename)
        if not path.is_file():
            raise FileNotFoundError("O arquivo CSV selecionado não foi encontrado.")

        current_records = self.store.list("registros")

        try:
            with path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file, delimiter=";")
                headers = [str(header or "").strip() for header in (reader.fieldnames or [])]

                if headers == EXTENDED_HEADERS:
                    return self._import_extended(reader, current_records)
                if headers == LEGACY_HEADERS:
                    return self._import_legacy(reader, current_records)

                raise ValueError(
                    "Cabeçalho CSV inválido. O novo formato deve ser:\n"
                    + ";".join(EXTENDED_HEADERS)
                    + "\n\nO formato antigo com IDs também continua aceito."
                )
        except UnicodeDecodeError as exc:
            raise ValueError("Não foi possível ler o arquivo. Salve-o em UTF-8.") from exc
