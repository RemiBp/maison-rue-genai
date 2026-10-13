import json
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from unittest.mock import patch
from http.server import ThreadingHTTPServer
import server

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True)
        cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.http.server_port}/api/triage'
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown(); cls.http.server_close(); cls.thread.join()
    def call(self,body,origin=None):
        headers={'Content-Type':'application/json'}
        if origin: headers['Origin']=origin
        req=Request(self.url,data=json.dumps(body).encode(),headers=headers)
        try:
            with urlopen(req) as r: return r.status,json.load(r)
        except HTTPError as r:
            with r: return r.code,json.load(r)
    def test_unknown_order_baseline(self):
        status,r=self.call({'text':'Where is A999?','engine':'baseline'})
        self.assertEqual(status,200); self.assertEqual(r['decisions'][0]['evidence'],[])
        self.assertIn('not in the supplied snapshot',r['decisions'][0]['customer_reply'])
    def test_invalid_input_never_calls_model(self):
        with patch('server.predict') as model:
            for body in [{'text':'','engine':'codex'},{'text':[],'engine':'codex'},{'text':'hello','engine':'unknown'}]:
                self.assertEqual(self.call(body)[0],400)
            model.assert_not_called()
    def test_foreign_origin(self):
        with patch('server.predict') as model:
            self.assertEqual(self.call({'text':'hello','engine':'codex'},'https://example.com')[0],403)
            model.assert_not_called()
    def test_timeout_has_no_fallback(self):
        with patch('server.predict',side_effect=RuntimeError('timeout')):
            status,r=self.call({'text':'hello','engine':'codex'})
            self.assertEqual(status,503); self.assertNotIn('decisions',r)
    def test_busy_model(self):
        server.GATE.acquire()
        try: self.assertEqual(self.call({'text':'hello','engine':'codex'})[0],409)
        finally: server.GATE.release()
if __name__=='__main__': unittest.main()
