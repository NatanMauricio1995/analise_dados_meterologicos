"""Filtros, estatísticas e comparações dos dados meteorológicos."""

from datetime import datetime, time


def parse_stored_datetime(value):
    return datetime.fromisoformat(value)


def parse_date_range(start_text="", end_text=""):
    start = None
    end = None
    if start_text.strip():
        start = datetime.strptime(start_text.strip(), "%d-%m-%Y").replace(
            hour=0, minute=0, second=0
        )
    if end_text.strip():
        end = datetime.strptime(end_text.strip(), "%d-%m-%Y").replace(
            hour=23, minute=59, second=59
        )
    if start and end and start > end:
        raise ValueError("A data inicial deve ser anterior ou igual à data final.")
    return start, end


def filter_records(records, point_id=None, start=None, end=None, source_id=None):
    result = []
    for record in records:
        if point_id is not None and int(record["ponto_observacao_id"]) != int(point_id):
            continue
        if source_id is not None and int(record['fonte_dados_id']) != int(source_id):
            continue
        moment = parse_stored_datetime(record["data_hora"])
        if start and moment < start:
            continue
        if end and moment > end:
            continue
        result.append(record)
    return sorted(result, key=lambda item: item["data_hora"])


def summarize(records):
    if not records:
        return None
    sources = {int(r['fonte_dados_id']) for r in records}
    points = {int(r['ponto_observacao_id']) for r in records}
    # Nunca somar fontes distintas como se fossem a mesma medição.
    rain_is_comparable = len(sources) == 1 and len(points) == 1
    temperatures = [float(item["temperatura"]) for item in records]
    humidities = [float(item["umidade"]) for item in records]
    rainfall = [float(item["precipitacao"]) for item in records]
    return {
        "quantidade": len(records),
        "temperatura_media": sum(temperatures) / len(temperatures),
        "temperatura_minima": min(temperatures),
        "temperatura_maxima": max(temperatures),
        "umidade_media": sum(humidities) / len(humidities),
        "umidade_minima": min(humidities),
        "umidade_maxima": max(humidities),
        "precipitacao_total": sum(rainfall) if rain_is_comparable else None,
        "precipitacao_maxima": max(rainfall),
        "fontes_distintas": len(sources),
        "aviso_precipitacao": None if rain_is_comparable else "Selecione um único ponto e uma única fonte para calcular a chuva acumulada.",
    }
