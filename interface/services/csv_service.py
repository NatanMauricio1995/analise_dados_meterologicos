"""Importação CSV com validação linha a linha e relatório de rejeições."""

import csv
from pathlib import Path

from .validators import ValidationError, validate_record

EXPECTED_HEADERS = [
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

    def import_file(self, filename):
        path = Path(filename)
        if not path.is_file():
            raise FileNotFoundError("O arquivo CSV selecionado não foi encontrado.")

        points = self.store.list("pontos")
        sources = self.store.list("fontes")
        current_records = self.store.list("registros")
        point_ids = {int(item["id"]) for item in points}
        source_ids = {int(item["id"]) for item in sources}

        existing_keys = {
            (int(item["ponto_observacao_id"]), int(item["fonte_dados_id"]), item["data_hora"])
            for item in current_records
        }
        seen_keys = set(existing_keys)
        accepted = []
        rejected = []

        try:
            with path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file, delimiter=";")
                headers = [str(h or "").strip() for h in (reader.fieldnames or [])]
                if headers != EXPECTED_HEADERS:
                    raise ValueError(
                        "Cabeçalho CSV inválido. Esperado: " + ";".join(EXPECTED_HEADERS)
                    )

                for line_number, row in enumerate(reader, start=2):
                    try:
                        if None in row and row[None]:
                            raise ValidationError("A linha possui mais colunas do que o cabeçalho CSV.")
                        values = {str(k).strip(): str(v or "").strip() for k, v in row.items() if k is not None}
                        normalized = validate_record(values, point_ids, source_ids)
                        key = (
                            normalized["ponto_observacao_id"],
                            normalized["fonte_dados_id"],
                            normalized["data_hora"],
                        )
                        if key in seen_keys:
                            raise ValidationError(
                                "Registro duplicado para a mesma fonte, ponto e data/hora."
                            )
                        seen_keys.add(key)
                        accepted.append(normalized)
                        rejected.append({
                            "linha": line_number,
                            "status": "IMPORTADA",
                            "motivo": "Registro validado.",
                        })
                    except (ValidationError, TypeError, ValueError) as exc:
                        rejected.append({
                            "linha": line_number,
                            "status": "REJEITADA",
                            "motivo": str(exc),
                        })
        except UnicodeDecodeError as exc:
            raise ValueError("Não foi possível ler o arquivo. Salve-o em UTF-8.") from exc

        if accepted:
            self.store.add_many("registros", accepted)

        return {
            "importadas": len(accepted),
            "rejeitadas": sum(1 for row in rejected if row["status"] == "REJEITADA"),
            "linhas": rejected,
        }
