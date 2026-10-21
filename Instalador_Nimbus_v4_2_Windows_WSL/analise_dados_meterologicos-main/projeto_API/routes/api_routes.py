"""API REST completa do Nimbus, com importação de observações em JSON."""
from datetime import datetime
from decimal import Decimal
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from entities.ponto_observacao import PontoObservacao
from entities.fonte_dados import FonteDados
from entities.registro_meteorologico import RegistroMeteorologico
from services.ponto_observacao_service import PontoObservacaoService
from services.fonte_dados_service import FonteDadosService
from services.registro_meteorologico_service import RegistroMeteorologicoService
from exceptions.erros import RecursoNaoEncontradoError
from shared.json_service import JSONImportService
from shared.statistics import filter_records, summarize, parse_date_range

api_bp=Blueprint('nimbus_api',__name__,url_prefix='/api')
RESOURCES={
  'pontos-observacao': (PontoObservacaoService,'ponto_observacao_id'),
  'fontes-dados': (FonteDadosService,'fonte_dados_id'),
  'registros': (RegistroMeteorologicoService,'registro_meteorologico_id'),
}

def as_json(model):
    result={}
    for column in model.__table__.columns:
        value=getattr(model,column.name)
        if isinstance(value,Decimal): value=str(value)
        if isinstance(value,datetime): value=value.isoformat(timespec='seconds')
        result[column.name]=value
    return result

def handle(operation):
    session=current_app.config['NIMBUS_SESSION_FACTORY']()
    try:
        return operation(session)
    except RecursoNaoEncontradoError as exc:
        session.rollback();return jsonify({'erro':str(exc)}),404
    except ValueError as exc:
        session.rollback()
        status=409 if 'associad' in str(exc).lower() or 'restrição' in str(exc).lower() else 400
        return jsonify({'erro':str(exc)}),status
    except IntegrityError:
        session.rollback();return jsonify({'erro':'Conflito de unicidade ou integridade referencial.'}),409
    except SQLAlchemyError:
        session.rollback();return jsonify({'erro':'Erro de acesso ao banco de dados.'}),500
    finally:
        session.close()

@api_bp.route('/<resource>',methods=['GET','POST'])
def collection(resource):
    if resource not in RESOURCES:return jsonify({'erro':'Recurso não encontrado.'}),404
    service_type,_=RESOURCES[resource]
    if request.method=='POST':
        payload=request.get_json(silent=True)
        if not isinstance(payload,dict):return jsonify({'erro':'Envie um objeto JSON.'}),400
        return handle(lambda s: (jsonify(as_json(service_type(s).criar(payload))),201))
    def list_items(s):
        items=service_type(s).listar_todos()
        if resource=='registros':
            pid=request.args.get('ponto_observacao_id',type=int)
            sid=request.args.get('fonte_dados_id',type=int)
            start=request.args.get('inicio');end=request.args.get('fim')
            # Datas são YYYY-MM-DD, não DD-MM-AAAA.
            if start or end:
                try:
                    start_dt=datetime.strptime(start,'%Y-%m-%d') if start else None
                    end_dt=datetime.strptime(end,'%Y-%m-%d').replace(hour=23,minute=59,second=59) if end else None
                except ValueError as exc:raise ValueError('Use início e fim como YYYY-MM-DD.') from exc
            else:start_dt=end_dt=None
            return jsonify(filter_records([as_json(v) for v in items],pid,start_dt,end_dt,sid)),200
        return jsonify([as_json(v) for v in items]),200
    return handle(list_items)

@api_bp.route('/<resource>/<int:item_id>',methods=['GET','PUT','DELETE'])
def individual(resource,item_id):
    if resource not in RESOURCES:return jsonify({'erro':'Recurso não encontrado.'}),404
    cls,_=RESOURCES[resource]
    def action(s):
        service=cls(s)
        if request.method=='GET':return jsonify(as_json(service.buscar_por_id(item_id))),200
        if request.method=='DELETE':
            service.excluir(item_id)
            return jsonify({'mensagem':'Excluído com sucesso.'}),200
        payload=request.get_json(silent=True)
        if not isinstance(payload,dict):raise ValueError('Envie um objeto JSON.')
        return jsonify(as_json(service.atualizar(item_id,payload))),200
    return handle(action)

class ORMImportStore:
    """Porta de armazenamento em lote com transação única no MySQL."""
    models={'pontos':(PontoObservacao,'ponto_observacao_id'),
            'fontes':(FonteDados,'fonte_dados_id'),
            'registros':(RegistroMeteorologico,'registro_meteorologico_id')}
    def __init__(self,session):
        self.session=session
        self.cache={}
    def list(self,name):
        if name not in self.cache:
            cls,key=self.models[name]
            self.cache[name]=[{'id':getattr(obj,key),**{
                k:(v.isoformat(sep=' ',timespec='seconds') if isinstance(v,datetime) else str(v) if isinstance(v,Decimal) else v)
                for k,v in as_json(obj).items() if k!=key}}
                for obj in self.session.query(cls).all()]
        return self.cache[name]
    def next_id(self,name):
        return max((int(x['id']) for x in self.list(name)),default=0)+1
    def save_import(self,points,sources,records):
        point_ids={};source_ids={}
        for p in points:
            cls=PontoObservacao
            obj=cls(**{k:v for k,v in p.items() if k!='id'})
            self.session.add(obj);self.session.flush()
            point_ids[p['id']]=obj.ponto_observacao_id
        for src in sources:
            obj=FonteDados(**{k:v for k,v in src.items() if k!='id'})
            self.session.add(obj);self.session.flush()
            source_ids[src['id']]=obj.fonte_dados_id
        for rec in records:
            values=rec.copy()
            values['ponto_observacao_id']=point_ids.get(values['ponto_observacao_id'],values['ponto_observacao_id'])
            values['fonte_dados_id']=source_ids.get(values['fonte_dados_id'],values['fonte_dados_id'])
            values['data_hora']=datetime.fromisoformat(values['data_hora'])
            self.session.add(RegistroMeteorologico(**values))
        self.session.commit()

@api_bp.post('/importacoes/json')
def json_import():
    doc=request.get_json(silent=True)
    if not isinstance(doc,dict):return jsonify({'erro':'Envie um JSON com a chave observacoes.'}),400
    return handle(lambda s:(jsonify(JSONImportService(ORMImportStore(s)).import_document(doc)),200))

@api_bp.get('/analises')
def analysis():
    def do(s):
        rows=[as_json(x) for x in RegistroMeteorologicoService(s).listar_todos()]
        pid=request.args.get('ponto_observacao_id',type=int)
        sid=request.args.get('fonte_dados_id',type=int)
        start=request.args.get('inicio');end=request.args.get('fim')
        try:
            a,b=parse_date_range(datetime.strptime(start,'%Y-%m-%d').strftime('%d-%m-%Y') if start else '',
                                 datetime.strptime(end,'%Y-%m-%d').strftime('%d-%m-%Y') if end else '')
        except ValueError as exc:raise ValueError('Datas inválidas. Use YYYY-MM-DD.') from exc
        filtered=filter_records(rows,pid,a,b,sid)
        return jsonify({'total':len(filtered),'estatisticas':summarize(filtered)}),200
    return handle(do)
