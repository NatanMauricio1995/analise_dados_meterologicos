"""Validações centrais das regras de negócio do Nimbus."""

import math
from datetime import datetime
from zoneinfo import ZoneInfo


def local_now():
    """Retorna o horário local brasileiro sem informação de fuso no valor."""
    try:
        return datetime.now(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None)
    except Exception:
        return datetime.now()


class ValidationError(ValueError):
    pass


def parse_number(value, field_name):
    try:
        number = float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} deve ser um número válido.")
    if not math.isfinite(number):
        raise ValidationError(f"{field_name} deve ser um número finito.")
    return number


def validate_point(values):
    required = ("nome", "latitude", "longitude", "cidade", "estado")
    if any(not str(values.get(key, "")).strip() for key in required):
        raise ValidationError("Todos os campos do ponto de observação são obrigatórios.")

    latitude = parse_number(values["latitude"], "Latitude")
    longitude = parse_number(values["longitude"], "Longitude")
    if not -90 <= latitude <= 90:
        raise ValidationError("Latitude inválida: utilize um valor entre -90 e 90 graus.")
    if not -180 <= longitude <= 180:
        raise ValidationError("Longitude inválida: utilize um valor entre -180 e 180 graus.")

    state = str(values["estado"]).strip().upper()
    if len(state) != 2 or not state.isascii() or not state.isalpha():
        raise ValidationError("Estado inválido: informe uma sigla de duas letras, como RJ.")

    return {
        "nome": str(values["nome"]).strip().upper(),
        "latitude": f"{latitude:.6f}",
        "longitude": f"{longitude:.6f}",
        "cidade": str(values["cidade"]).strip().upper(),
        "estado": state,
    }


def validate_source(values):
    name = str(values.get("nome", "")).strip()
    kind = str(values.get("tipo", "")).strip()
    description = str(values.get("descricao", "")).strip()
    if not name or not kind:
        raise ValidationError("Nome e tipo da fonte são obrigatórios.")
    return {
        "nome": name.upper(),
        "tipo": kind.upper(),
        "descricao": description.upper(),
    }


def parse_ui_datetime(value):
    """Recebe DD-MM-AAAA HH:MM e devolve datetime."""
    try:
        parsed = datetime.strptime(value.strip(), "%d-%m-%Y %H:%M")
    except ValueError as exc:
        raise ValidationError(
            "Data/hora inválida. Use DD-MM-AAAA HH:MM, por exemplo 18-10-2026 20:00."
        ) from exc
    if parsed > local_now():
        raise ValidationError("A data e hora da observação não podem estar no futuro.")
    return parsed


def parse_csv_datetime(value):
    try:
        parsed = datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        raise ValidationError("data_hora deve seguir AAAA-MM-DD HH:MM:SS.") from exc
    if parsed > local_now():
        raise ValidationError("A data e hora da observação não podem estar no futuro.")
    return parsed


def validate_record(values, point_ids, source_ids):
    required = (
        "ponto_observacao_id", "fonte_dados_id", "data_hora",
        "temperatura", "umidade", "precipitacao",
    )
    if any(str(values.get(key, "")).strip() == "" for key in required):
        raise ValidationError("Todos os campos do registro meteorológico são obrigatórios.")

    try:
        point_id = int(values["ponto_observacao_id"])
        source_id = int(values["fonte_dados_id"])
    except (TypeError, ValueError) as exc:
        raise ValidationError("Selecione um ponto e uma fonte válidos.") from exc

    if point_id not in point_ids:
        raise ValidationError("O ponto de observação selecionado não existe.")
    if source_id not in source_ids:
        raise ValidationError("A fonte de dados selecionada não existe.")

    when = values["data_hora"]
    if isinstance(when, datetime):
        parsed_date = when
        if parsed_date > datetime.now():
            raise ValidationError("A data e hora da observação não podem estar no futuro.")
    else:
        raw = str(when).strip()
        if len(raw) == 19 and raw[4:5] == "-":
            parsed_date = parse_csv_datetime(raw)
        else:
            parsed_date = parse_ui_datetime(raw)

    temperature = parse_number(values["temperatura"], "Temperatura")
    humidity = parse_number(values["umidade"], "Umidade")
    rain = parse_number(values["precipitacao"], "Precipitação")

    if not -90 <= temperature <= 60:
        raise ValidationError("Temperatura inválida: utilize um valor entre -90 °C e 60 °C.")
    if not 0 <= humidity <= 100:
        raise ValidationError("Umidade inválida: utilize um valor entre 0% e 100%.")
    if rain < 0:
        raise ValidationError("Precipitação inválida: o valor não pode ser negativo.")

    return {
        "ponto_observacao_id": point_id,
        "fonte_dados_id": source_id,
        "data_hora": parsed_date.strftime("%Y-%m-%d %H:%M:%S"),
        "temperatura": f"{temperature:.2f}",
        "umidade": f"{humidity:.2f}",
        "precipitacao": f"{rain:.2f}",
    }
