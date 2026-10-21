"""Adapter CRUD para a API REST; mantém interface Tkinter sem mudança de telas."""
import os
from pathlib import Path
from .api import APIClient

class ApiDataStore:
    routes={'pontos':'pontos-observacao','fontes':'fontes-dados','registros':'registros'}
    idfields={'pontos':'ponto_observacao_id','fontes':'fonte_dados_id','registros':'registro_meteorologico_id'}
    def __init__(self,address=None):
        self.client=APIClient(address or os.environ.get('NIMBUS_API_URL','http://127.0.0.1:5000'))
        self.data_dir=Path(__file__).resolve().parents[1]/'dados'
        self.data_dir.mkdir(exist_ok=True,parents=True)
        self.client.get('/health')
    def _map(self,name,row):
        row=row.copy();row['id']=row.pop(self.idfields[name]);
        if name=='registros':row['data_hora']=row['data_hora'].replace('T',' ')
        return row
    def list(self,name):
        return [self._map(name,x) for x in self.client.get('/api/'+self.routes[name])]
    def next_id(self,name):
        return max((int(x['id']) for x in self.list(name)),default=0)+1
    def add(self,name,values):
        return self._map(name,self.client.post('/api/'+self.routes[name],values))
    def update(self,name,item_id,values):
        return self._map(name,self.client.put(f'/api/{self.routes[name]}/{item_id}',values))
    def delete(self,name,item_id):
        return self.client.delete(f'/api/{self.routes[name]}/{item_id}')
    def import_json_document(self,doc):
        return self.client.post('/api/importacoes/json',doc)
