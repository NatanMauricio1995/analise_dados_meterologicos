import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request,urlopen
from interface.services.upload_server import BrowserJSONUploadServer

class BrowserJSONUploadServerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        root=Path(self.temp.name)/'interface'
        resources=root/'recursos';resources.mkdir(parents=True)
        self.dest=root/'dados'/'importacoes';self.dest.mkdir(parents=True)
        (resources/'nimbus_logo.png').write_bytes(b'fake-png')
        (resources/'upload.html').write_text('<input type="file" accept=".json,application/json">__TOKEN__',encoding='utf8')
        self.server=BrowserJSONUploadServer(self.dest,host='127.0.0.1',port=0).start()
        self.url=f'http://127.0.0.1:{self.server.port}'
    def tearDown(self):
        self.server.stop();self.temp.cleanup()
    def send(self,filename,body,token=None):
        return urlopen(Request(self.url+'/upload?filename='+filename,data=body,
                headers={'X-Nimbus-Token':token or self.server.token},method='POST'))
    def test_portal_and_logo(self):
        self.assertIn('type="file"',urlopen(self.url+'/').read().decode())
        self.assertEqual(urlopen(self.url+'/logo.png').read(),b'fake-png')
    def test_valid_json(self):
        content=json.dumps({'observacoes':[]}).encode()
        with self.send('data.json',content) as reply:
            self.assertEqual(reply.status,201)
        self.assertEqual((self.dest/'data.json').read_bytes(),content)
    def test_rejects_bad_token(self):
        with self.assertRaises(HTTPError) as ctx:self.send('data.json',b'{}','incorrect')
        self.assertEqual(ctx.exception.code,403)
    def test_rejects_csv_and_malformed_json(self):
        for name,content,expected in (('data.csv',b'{}',415),('data.json',b'{',400),('data.json',b'[]',400)):
            with self.subTest(name=name),self.assertRaises(HTTPError) as ctx:self.send(name,content)
            self.assertEqual(ctx.exception.code,expected)
