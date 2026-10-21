"""Validações idênticas na interface e nas importações da API."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UF = set("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())

class ValidationError(ValueError):
    pass

def local_now():
    """Hora civil de São Paulo, inclusive no Windows sem base IANA instalada.

    No Windows, zoneinfo pode falhar sem o pacote tzdata. O Brasil aboliu
    o horário de verão em 2019; UTC-03:00 permite validar o instante atual
    mesmo sem tzdata. Com a base IANA disponível, a usamos normalmente.
    """
    try:
        sao_paulo = ZoneInfo("America/Sao_Paulo")
    except ZoneInfoNotFoundError:
        sao_paulo = timezone(timedelta(hours=-3))
    return datetime.now(sao_paulo).replace(tzinfo=None)

def decimal_value(value, label, minimum, maximum, precision):
    if isinstance(value, bool) or value is None or str(value).strip() == "":
        raise ValidationError(f"{label}: informe um número válido.")
    try:
        dec = Decimal(str(value).strip().replace(",", "."))
    except (ValueError, InvalidOperation, TypeError) as exc:
        raise ValidationError(f"{label}: informe um número válido.") from exc
    if not dec.is_finite() or not Decimal(str(minimum)) <= dec <= Decimal(str(maximum)):
        raise ValidationError(f"{label}: valor fora do intervalo {minimum} a {maximum}.")
    if dec != dec.quantize(Decimal(1).scaleb(-precision)):
        raise ValidationError(f"{label}: máximo de {precision} casas decimais; não arredondamos medições.")
    return dec

def parse_number(value, field_name):
    return float(decimal_value(value,field_name,'-999999999','999999999',6))

def validate_point(values):
    if not isinstance(values,dict):
        raise ValidationError("O ponto deve ser um objeto JSON.")
    name = str(values.get('nome') or '').strip().upper()
    city = str(values.get('cidade') or '').strip().upper()
    state = str(values.get('estado') or '').strip().upper()
    if not name:
        raise ValidationError("O nome do ponto é obrigatório.")
    if len(name)>100 or len(city)>100:
        raise ValidationError("Nome do ponto e cidade aceitam até 100 caracteres.")
    if state and state not in UF:
        raise ValidationError("Estado inválido: informe uma UF brasileira (ex.: RJ).")
    lat=decimal_value(values.get('latitude'),'Latitude',-90,90,6)
    lon=decimal_value(values.get('longitude'),'Longitude',-180,180,6)
    return dict(nome=name, latitude=f'{lat:.6f}', longitude=f'{lon:.6f}', cidade=city or None, estado=state or None)

def validate_source(values):
    if not isinstance(values,dict):
        raise ValidationError("A fonte deve ser um objeto JSON.")
    name=str(values.get('nome') or '').strip().upper()
    kind=str(values.get('tipo') or '').strip().upper()
    desc=str(values.get('descricao') or '').strip().upper()
    if not name or not kind:
        raise ValidationError("Nome e tipo da fonte são obrigatórios.")
    if len(name)>100 or len(kind)>50 or len(desc)>255:
        raise ValidationError("Fonte excede o limite: nome 100, tipo 50, descrição 255 caracteres.")
    return dict(nome=name,tipo=kind,descricao=desc or None)

def parse_ui_datetime(value):
    try:
        parsed=datetime.strptime(str(value).strip(),'%d-%m-%Y %H:%M')
    except (TypeError,ValueError) as exc:
        raise ValidationError('Use DD-MM-AAAA HH:MM.') from exc
    if parsed>local_now():
        raise ValidationError('Data/hora futura não é permitida.')
    return parsed

def parse_json_datetime(value):
    if isinstance(value,datetime):
        parsed=value
    else:
        try:
            parsed=datetime.fromisoformat(str(value).strip())
        except (ValueError,TypeError) as exc:
            raise ValidationError('data_hora deve usar ISO 8601, exemplo 2026-10-19T14:30:00.') from exc
    if parsed.tzinfo is not None:
        raise ValidationError('data_hora deve informar horário civil de America/Sao_Paulo sem offset.')
    if parsed>local_now():
        raise ValidationError('A data e hora da observação não podem estar no futuro.')
    return parsed

def parse_csv_datetime(value):
    return parse_json_datetime(value)

def validate_record(values,point_ids,source_ids):
    required=('ponto_observacao_id','fonte_dados_id','data_hora','temperatura','umidade','precipitacao')
    if not isinstance(values,dict) or any(values.get(k) in (None,'') for k in required):
        raise ValidationError('Todos os campos do registro meteorológico são obrigatórios.')
    try:
        pid=int(values['ponto_observacao_id']);sid=int(values['fonte_dados_id'])
    except (TypeError,ValueError) as exc:
        raise ValidationError('Ponto e fonte devem ter identificadores inteiros.') from exc
    if pid not in point_ids or sid not in source_ids:
        raise ValidationError('Ponto ou fonte inexistente.')
    raw=values['data_hora']
    when=parse_ui_datetime(raw) if isinstance(raw,str) and len(raw)>=10 and raw[2:3]=='-' else parse_json_datetime(raw)
    t=decimal_value(values['temperatura'],'Temperatura',-90,60,2)
    h=decimal_value(values['umidade'],'Umidade',0,100,2)
    rain=decimal_value(values['precipitacao'],'Precipitação',0,'999999.99',2)
    return dict(ponto_observacao_id=pid,fonte_dados_id=sid,data_hora=when.strftime('%Y-%m-%d %H:%M:%S'),temperatura=f'{t:.2f}',umidade=f'{h:.2f}',precipitacao=f'{rain:.2f}')
