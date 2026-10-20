"""Importa o novo CSV e cria os pontos e as fontes necessários."""

import csv
from pathlib import Path

from .validators import ValidationError, validate_point, validate_source, validate_record

HEADERS = [
    "ponto_nome", "latitude", "longitude", "cidade", "estado",
    "fonte_nome", "fonte_tipo", "fonte_descricao",
    "data_hora", "temperatura", "umidade", "precipitacao",
]


def point_key(point):
    return (
        point["nome"].upper(), float(point["latitude"]),
        float(point["longitude"]), point["cidade"].upper(), point["estado"].upper()
    )


def source_key(source):
    return source["nome"].upper(), source["tipo"].upper()


class CSVImportService:
    def __init__(self, store):
        self.store = store

    def import_file(self, filename):
        path = Path(filename)
        if not path.is_file():
            raise FileNotFoundError("O arquivo CSV não foi encontrado.")

        try:
            with path.open(encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file, delimiter=";")
                headers = [str(item or "").strip() for item in (reader.fieldnames or [])]
                if headers != HEADERS:
                    raise ValueError("Cabeçalho inválido. Baixe e utilize o modelo CSV do Nimbus.")
                return self._import_rows(reader)
        except UnicodeDecodeError as exc:
            raise ValueError("O arquivo deve estar salvo em UTF-8.") from exc

    def _import_rows(self, reader):
        points = self.store.list("pontos")
        sources = self.store.list("fontes")
        records = self.store.list("registros")

        point_ids = {point_key(p): int(p["id"]) for p in points}
        source_ids = {source_key(s): int(s["id"]) for s in sources}
        new_points, new_sources, accepted, report = {}, {}, [], []
        duplicates = {
            (int(r["ponto_observacao_id"]), int(r["fonte_dados_id"]), r["data_hora"])
            for r in records
        }

        for number, row in enumerate(reader, start=2):
            try:
                if row.get(None):
                    raise ValidationError("A linha tem mais colunas do que o cabeçalho.")

                point = validate_point({
                    "nome": row.get("ponto_nome", ""),
                    "latitude": row.get("latitude", ""),
                    "longitude": row.get("longitude", ""),
                    "cidade": row.get("cidade", ""),
                    "estado": row.get("estado", ""),
                })
                source = validate_source({
                    "nome": row.get("fonte_nome", ""),
                    "tipo": row.get("fonte_tipo", ""),
                    "descricao": row.get("fonte_descricao", ""),
                })

                pkey, skey = point_key(point), source_key(source)
                point_id = point_ids.get(pkey)
                source_id = source_ids.get(skey)

                # Calcula IDs novos sem gravar cadastros antes de validar a observação.
                if point_id is None:
                    point_id = self.store.next_id("pontos") + len(new_points)
                if source_id is None:
                    source_id = self.store.next_id("fontes") + len(new_sources)

                record = validate_record({
                    "ponto_observacao_id": point_id,
                    "fonte_dados_id": source_id,
                    "data_hora": row.get("data_hora", ""),
                    "temperatura": row.get("temperatura", ""),
                    "umidade": row.get("umidade", ""),
                    "precipitacao": row.get("precipitacao", ""),
                }, {point_id}, {source_id})

                key = (point_id, source_id, record["data_hora"])
                if key in duplicates:
                    raise ValidationError("Registro duplicado para o mesmo ponto, fonte e horário.")

                duplicates.add(key)
                if pkey not in point_ids:
                    new_points[pkey] = point
                    point_ids[pkey] = point_id
                if skey not in source_ids:
                    new_sources[skey] = source
                    source_ids[skey] = source_id

                accepted.append(record)
                report.append({"linha": number, "status": "IMPORTADA", "motivo": "Observação validada."})

            except (ValidationError, TypeError, ValueError) as exc:
                report.append({"linha": number, "status": "REJEITADA", "motivo": str(exc)})

        # Salva apenas cadastros usados por observações válidas.
        old_data = {name: list(self.store.list(name)) for name in ("pontos", "fontes", "registros")}
        try:
            if new_points:
                self.store.add_many("pontos", list(new_points.values()))
            if new_sources:
                self.store.add_many("fontes", list(new_sources.values()))
            if accepted:
                self.store.add_many("registros", accepted)
        except OSError as exc:
            for name, rows in old_data.items():
                self.store.data[name] = rows
                try:
                    self.store._write(name)
                except OSError:
                    pass
            raise ValueError("Não foi possível salvar a importação. Verifique o armazenamento.") from exc

        imported = sum(row["status"] == "IMPORTADA" for row in report)
        return {
            "importadas": imported,
            "rejeitadas": len(report) - imported,
            "pontos_criados": len(new_points),
            "fontes_criadas": len(new_sources),
            "linhas": report,
        }
