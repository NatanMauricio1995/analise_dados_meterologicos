"""Importação estruturada de observações meteorológicas em JSON.

Formato: {"observacoes": [{"ponto": {...}, "fonte": {...}, "data_hora": ..., ...}]}.
Registros inválidos são reportados individualmente; novos cadastros só são criados
quando uma observação for válida. A gravação é delegada a save_import().
"""
import json
from pathlib import Path
from .validators import ValidationError, validate_point, validate_source, validate_record

MAX_OBSERVATIONS=50000
MAX_BYTES=15*1024*1024

def point_key(point):
    return (point['nome'].upper(),point['latitude'],point['longitude'],
            (point.get('cidade') or '').upper(),(point.get('estado') or '').upper())

def source_key(source):
    return (source['nome'].upper(),source['tipo'].upper())

class JSONImportService:
    def __init__(self, store):
        self.store=store

    def import_file(self, filename):
        path=Path(filename)
        if not path.is_file() or path.suffix.lower()!='.json':
            raise ValueError('Selecione um arquivo .json existente.')
        if path.stat().st_size>MAX_BYTES:
            raise ValueError('Arquivo JSON excede 15 MB.')
        try:
            with path.open(encoding='utf-8-sig') as f:
                document=json.load(f)
        except (json.JSONDecodeError,UnicodeDecodeError) as exc:
            raise ValueError(f'JSON inválido ou não codificado em UTF-8: {exc}') from exc
        return self.import_document(document)

    def import_document(self,document):
        if hasattr(self.store, "import_json_document"):
            return self.store.import_json_document(document)
        if not isinstance(document,dict) or not isinstance(document.get('observacoes'),list):
            raise ValueError('O JSON deve conter o objeto {"observacoes": [...]} com uma lista.')
        rows=document['observacoes']
        if len(rows)>MAX_OBSERVATIONS:
            raise ValueError('Limite de 50.000 observações por importação.')
        if not rows:
            return dict(importadas=0,rejeitadas=0,duplicadas=0,pontos_criados=0,fontes_criadas=0,linhas=[])
        points=self.store.list('pontos');sources=self.store.list('fontes');records=self.store.list('registros')
        point_ids={point_key(p):int(p['id']) for p in points}
        source_ids={source_key(s):int(s['id']) for s in sources}
        new_points,new_sources,accepted,report={},{},[],[]
        ignored_duplicates=0
        duplicates={(int(x['ponto_observacao_id']),int(x['fonte_dados_id']),x['data_hora']) for x in records}
        for number,row in enumerate(rows,1):
            try:
                if not isinstance(row,dict):
                    raise ValidationError('Observação deve ser um objeto JSON.')
                allowed={'ponto','fonte','data_hora','temperatura','umidade','precipitacao'}
                extra=set(row)-allowed
                if extra:
                    raise ValidationError('Campos não permitidos: '+', '.join(sorted(extra)))
                point=validate_point(row.get('ponto'))
                source=validate_source(row.get('fonte'))
                pkey,skey=point_key(point),source_key(source)
                pid=point_ids.get(pkey,self.store.next_id('pontos')+len(new_points))
                sid=source_ids.get(skey,self.store.next_id('fontes')+len(new_sources))
                rec=validate_record(dict(ponto_observacao_id=pid,fonte_dados_id=sid,
                    data_hora=row.get('data_hora'),temperatura=row.get('temperatura'),
                    umidade=row.get('umidade'),precipitacao=row.get('precipitacao')),{pid},{sid})
                key=(pid,sid,rec['data_hora'])
                if key in duplicates:
                    ignored_duplicates+=1
                    report.append(dict(linha=number,status='DUPLICADA',
                        motivo='Esta observação já foi importada (mesmo ponto, fonte e horário).'))
                    continue
                if pkey not in point_ids:
                    new_points[pkey]={'id':pid,**point};point_ids[pkey]=pid
                if skey not in source_ids:
                    new_sources[skey]={'id':sid,**source};source_ids[skey]=sid
                accepted.append(rec);duplicates.add(key)
                report.append(dict(linha=number,status='IMPORTADA',motivo='Observação validada.'))
            except (ValidationError,TypeError,ValueError) as exc:
                report.append(dict(linha=number,status='REJEITADA',motivo=str(exc)))
        if accepted:
            self.store.save_import(list(new_points.values()),list(new_sources.values()),accepted)
        return dict(importadas=len(accepted),rejeitadas=len(report)-len(accepted)-ignored_duplicates,
                    duplicadas=ignored_duplicates,
                    pontos_criados=len(new_points),fontes_criadas=len(new_sources),linhas=report)
