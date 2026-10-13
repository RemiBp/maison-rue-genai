"""Local demonstration server; standard library only, no external write actions."""
import json
import threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from workflow import baseline
from model import predict

ROOT=Path(__file__).parent
GATE=threading.Lock()
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def send(self,status,body,content_type='application/json; charset=utf-8'):
        if not isinstance(body,bytes): body=json.dumps(body,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers(); self.wfile.write(body)
    def allowed(self):
        expected=f'127.0.0.1:{self.server.server_port}'
        host=self.headers.get('Host','')
        origin=self.headers.get('Origin')
        return host==expected and (not origin or origin==f'http://{expected}')
    def do_GET(self):
        if not self.allowed(): return self.send(403,{'error':'Local requests only'})
        path=urlparse(self.path).path
        if path=='/': return self.send(200,(ROOT/'index.html').read_bytes(),'text/html; charset=utf-8')
        if path=='/api/results':
            f=ROOT/'evaluation.json'
            report=json.loads(f.read_text()) if f.exists() else {'rows':[]}
            audit=ROOT/'audit.json'
            import hashlib
            meta=ROOT/'audit_metadata.json'
            valid=audit.exists() and meta.exists() and json.loads(meta.read_text()).get('evaluation_sha256')==hashlib.sha256(f.read_bytes()).hexdigest()
            report['audit']=json.loads(audit.read_text()) if valid else {}
            return self.send(200,report)
        if path=='/api/sources': return self.send(200,json.loads((ROOT/'knowledge.json').read_text()))
        if path=='/appendix': return self.send(200,(ROOT/'appendix.html').read_bytes(),'text/html; charset=utf-8')
        if path=='/api/cases': return self.send(200,json.loads((ROOT/'cases.json').read_text()))
        return self.send(404,{'error':'Not found'})
    def do_POST(self):
        if not self.allowed(): return self.send(403,{'error':'Local requests only'})
        if self.path!='/api/triage': return self.send(404,{'error':'Not found'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<1 or length>16000: raise ValueError('Request too large')
            request=json.loads(self.rfile.read(length))
            text=request.get('text')
            if not isinstance(text,str) or not 1<=len(text.strip())<=4000:
                raise ValueError('Une demande de 1 à 4 000 caractères est nécessaire.')
            if request.get('engine') not in {'baseline','codex'}: raise ValueError('Invalid engine')
            if request['engine']=='baseline':
                import time
                start=time.perf_counter(); decision=baseline({'id':'demo','text':text})
                return self.send(200,{'decisions':[decision],'engine':'Template','elapsed_seconds':time.perf_counter()-start})
            if not GATE.acquire(blocking=False): return self.send(409,{'error':'Une analyse est déjà en cours.'})
            try: result=predict([{'id':'demo','text':text}])
            finally: GATE.release()
            return self.send(200,result)
        except (ValueError,json.JSONDecodeError):
            return self.send(400,{'error':'Demande invalide. Vérifie le texte et le moteur sélectionné.'})
        except RuntimeError as exc: return self.send(503,{'error':str(exc)})
        except Exception: return self.send(500,{'error':'Analyse interrompue. Aucune décision acceptée.'})

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8524)
    args=parser.parse_args()
    print(f'Demo: http://127.0.0.1:{args.port}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
