"""AIDOS Home 0.5: ingress application. Python standard library only.

Private settings remain under /data; Supervisor credential never sent to client.
"""
import json
import logging
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = os.getenv('AIDOS_HOST', '0.0.0.0')
PORT = int(os.getenv('AIDOS_PORT', '8099'))
DATA = Path(os.getenv('AIDOS_DATA_DIR', '/data'))
STATIC = Path(__file__).parent / 'static'
TOKEN = os.getenv('SUPERVISOR_TOKEN', '')
HA_URL = os.getenv('AIDOS_HA_URL', 'http://supervisor/core/api').rstrip('/')
API_TOKEN = os.getenv('AIDOS_HA_TOKEN', TOKEN)
LOG = logging.getLogger('aidos')
VALID_ID = re.compile(r'^[a-z][a-z0-9_]*\.[a-zA-Z0-9_]+$')
VALID_DOMAIN = re.compile(r'^[a-z][a-z0-9_]*$')
SENSITIVE_DOMAINS = {'lock','alarm_control_panel','cover','button','script','automation'}
DEFAULT = {
    'title': 'AIDOS Home', 'theme': 'dark', 'accent': '#4ec7c9',
    'pages': [
        {'id':'home','name':'Panoramica','icon':'⌂'},
        {'id':'cctv','name':'Telecamere','icon':'▣'},
        {'id':'heating','name':'Clima','icon':'♨'},
        {'id':'status','name':'Sicurezza e stato','icon':'◉'},
        {'id':'entertainment','name':'Multimedia','icon':'♫'},
        {'id':'lights','name':'Illuminazione','icon':'☀'},
        {'id':'statistics','name':'Statistiche','icon':'▥'},
    ],
    'cards': [],
    'layout': {},
    'notifications': {'enabled': False, 'service': 'persistent_notification.create',
                      'cooldown_seconds': 300, 'on_unavailable': True},
    'assistant': {'enabled': True, 'agent_id': ''},
}
LOCK = threading.RLock()


def clean_settings(obj):
    if not isinstance(obj, dict):
        raise ValueError('Configurazione non valida')
    result = json.loads(json.dumps(DEFAULT))
    result['title'] = str(obj.get('title', result['title']))[:80]
    result['theme'] = obj.get('theme') if obj.get('theme') in ('dark','light') else 'dark'
    accent = obj.get('accent', result['accent'])
    result['accent'] = accent if isinstance(accent, str) and re.fullmatch(r'#[0-9a-fA-F]{6}',accent) else '#4ec7c9'
    pages = obj.get('pages', result['pages'])
    if not isinstance(pages, list) or len(pages)>50: raise ValueError('Pagine non valide')
    ids = set()
    result['pages'] = []
    for p in pages:
        if not isinstance(p,dict):continue
        pid = str(p.get('id',''))[:40]
        if not re.fullmatch(r'[a-z0-9_-]+',pid) or pid in ids: continue
        ids.add(pid)
        result['pages'].append({'id':pid,'name':str(p.get('name','Pagina'))[:48], 'icon':str(p.get('icon','▣'))[:4]})
    layout = obj.get('layout', {})
    if isinstance(layout, dict):
        sanitized_layout={}
        for page_id, groups in layout.items():
            if page_id not in ids or not isinstance(groups, list): continue
            clean_groups=[]
            for group in groups[:40]:
                if not isinstance(group, list):continue
                cells=[]
                for cell in group[:8]:
                    if not isinstance(cell,list):continue
                    cells.append([str(cid)[:64] for cid in cell[:50] if isinstance(cid,str)])
                clean_groups.append(cells)
            sanitized_layout[page_id]=clean_groups
        result['layout']=sanitized_layout
    cards = obj.get('cards', [])
    if not isinstance(cards,list) or len(cards)>1000:raise ValueError('Troppe schede')
    result['cards'] = []
    seen=set()
    for c in cards:
        if not isinstance(c,dict):continue
        cid = str(c.get('id',''))[:64]
        eid = str(c.get('entity_id',''))[:120]
        page = str(c.get('page','home'))[:40]
        typ = str(c.get('type','entity'))[:30]
        if not re.fullmatch(r'[a-zA-Z0-9_-]+',cid) or cid in seen:continue
        if eid and not VALID_ID.fullmatch(eid): continue
        if page not in ids:continue
        seen.add(cid)
        result['cards'].append({'id':cid,'page':page,'type':typ,
            'title':str(c.get('title',''))[:80], 'entity_id':eid,
            'notify':bool(c.get('notify',False)),'notify_on_change':bool(c.get('notify_on_change',True)),
            'notify_state':str(c.get('notify_state',''))[:80],
            'span':2 if c.get('span')==2 else 1,
            'source_template':str(c.get('source_template',''))[:60]})
    noti=obj.get('notifications',{})
    if isinstance(noti,dict):
        service=str(noti.get('service','persistent_notification.create'))
        # Avoid arbitrary services: only notifications can be dispatched
        if service!='persistent_notification.create' and not re.fullmatch(r'notify\.[a-z0-9_]+',service):
            service='persistent_notification.create'
        result['notifications']={'enabled':bool(noti.get('enabled',False)),
           'service':service,'cooldown_seconds':max(30,min(86400,int(noti.get('cooldown_seconds',300)))),
           'on_unavailable':bool(noti.get('on_unavailable',True))}
    assist=obj.get('assistant',{})
    if isinstance(assist,dict):
        result['assistant']={'enabled':bool(assist.get('enabled',True)),
           'agent_id':str(assist.get('agent_id',''))[:120]}
    return result


def read_settings():
    with LOCK:
        path=DATA/'settings.json'
        if not path.exists():return json.loads(json.dumps(DEFAULT))
        return clean_settings(json.loads(path.read_text(encoding='utf-8')))


def write_settings(payload):
    cfg=clean_settings(payload)
    with LOCK:
        DATA.mkdir(parents=True,exist_ok=True)
        temp=DATA/'settings.json.tmp'
        temp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
        temp.replace(DATA/'settings.json')
    return cfg


def ha_request(method, path, body=None):
    if not API_TOKEN:raise RuntimeError('Token Home Assistant non disponibile')
    url=HA_URL+'/'+path.lstrip('/')
    b=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url,data=b,method=method,headers={
        'Authorization':'Bearer '+API_TOKEN,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=12) as res:
            data=res.read(2_000_000)
            if not data:return {}
            return json.loads(data)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'Home Assistant HTTP {e.code}') from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError('Home Assistant non raggiungibile') from e


def call_service(domain, service, fields):
    if not VALID_DOMAIN.fullmatch(domain) or not VALID_DOMAIN.fullmatch(service):
        raise ValueError('Servizio non valido')
    if not isinstance(fields,dict):raise ValueError('Dati servizio non validi')
    return ha_request('POST',f'services/{domain}/{service}',fields)


def notification_loop():
    previous={}
    last_sent={}
    initialized=False
    while True:
        try:
            cfg=read_settings()
            enabled=cfg['notifications']['enabled']
            monitored={c['entity_id']:c for c in cfg['cards'] if c['entity_id'] and c['notify']}
            if not enabled or not monitored:
                previous={}; initialized=False
                time.sleep(15);continue
            states=ha_request('GET','states')
            current={s['entity_id']:str(s['state']) for s in states if s.get('entity_id') in monitored}
            if initialized:
                for eid, new in current.items():
                    card=monitored[eid];old=previous.get(eid)
                    if old is None or old==new:continue
                    if new in ('unavailable','unknown') and not cfg['notifications']['on_unavailable']: continue
                    if card['notify_state'] and card['notify_state']!=new:continue
                    if not card['notify_on_change'] and not card['notify_state']:continue
                    key=(eid,new)
                    now=time.monotonic()
                    if now-last_sent.get(key,-1e10)<cfg['notifications']['cooldown_seconds']:continue
                    service=cfg['notifications']['service']
                    msg=f"{card['title'] or eid}: {old} → {new}"
                    dom,svc=service.split('.',1)
                    payload={'title':'AIDOS','message':msg} if dom=='persistent_notification' else {'message':msg,'title':'AIDOS'}
                    call_service(dom,svc,payload)
                    last_sent[key]=now
            previous=current;initialized=True
        except Exception as e:
            LOG.warning('Monitor notifiche: %s',e)
            initialized=False
        time.sleep(15)


class Handler(BaseHTTPRequestHandler):
    def respond(self,code,body):
        b=json.dumps(body,ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'")
        self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)

    def read_payload(self):
        n=int(self.headers.get('Content-Length','0'))
        if n>100_000:raise ValueError('Payload troppo grande')
        return json.loads(self.rfile.read(n) or b'{}')

    def do_GET(self):
        path=urllib.parse.urlsplit(self.path).path
        try:
            if path in ('/api/health','/health'):
                return self.respond(200,{'ok':True,'version':'0.5.0','ha_configured':bool(API_TOKEN)})
            if path=='/api/settings':return self.respond(200,read_settings())
            if path=='/api/states':return self.respond(200,ha_request('GET','states'))
            if path=='/api/agents':return self.respond(200,ha_request('GET','conversation/agents'))
            if path.startswith('/api/'):return self.respond(404,{'error':'Percorso inesistente'})
            asset={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/style.css':'style.css','/catalog.json':'catalog.json'}.get(path)
            if not asset:return self.respond(404,{'error':'Non trovato'})
            data=(STATIC/asset).read_bytes()
            self.send_response(200)
            self.send_header('Content-Type',{'index.html':'text/html; charset=utf-8','app.js':'application/javascript; charset=utf-8','style.css':'text/css; charset=utf-8','catalog.json':'application/json; charset=utf-8'}[asset])
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'")
            self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        except Exception as e:self.respond(502,{'error':str(e)})

    def do_POST(self):
        path=urllib.parse.urlsplit(self.path).path
        try:
            data=self.read_payload()
            if path=='/api/settings':return self.respond(200,write_settings(data))
            if path=='/api/command':
                domain=str(data.get('domain',''));service=str(data.get('service',''))
                entity=str(data.get('entity_id',''))
                if not VALID_ID.fullmatch(entity) or entity.split('.')[0]!=domain:
                    raise ValueError('Entità non valida')
                allowed={
                  'light':{'turn_on','turn_off','toggle'},'switch':{'turn_on','turn_off','toggle'},
                  'fan':{'turn_on','turn_off','toggle','set_percentage'},
                  'input_boolean':{'turn_on','turn_off','toggle'},
                  'climate':{'set_temperature','set_hvac_mode','turn_on','turn_off'},
                  'cover':{'open_cover','close_cover','stop_cover','set_cover_position'},
                  'lock':{'lock','unlock'},
                  'media_player':{'turn_on','turn_off','media_play_pause','volume_set'},
                  'vacuum':{'start','pause','return_to_base','stop'},
                  'scene':{'turn_on'},'script':{'turn_on'},'automation':{'trigger'},
                  'button':{'press'},'number':{'set_value'},'input_number':{'set_value'},
                  'select':{'select_option'},'input_select':{'select_option'},
                }
                if service not in allowed.get(domain,set()):raise ValueError('Comando non consentito')
                if domain in SENSITIVE_DOMAINS and not data.get('confirm'):
                    raise ValueError('Conferma obbligatoria per il comando')
                ext=data.get('data',{})
                if not isinstance(ext,dict) or len(ext)>12:raise ValueError('Parametri non validi')
                safe={k:v for k,v in ext.items() if k in ('brightness_pct','temperature','hvac_mode','position','percentage','volume_level','value','option') and isinstance(v,(str,int,float))}
                return self.respond(200,call_service(domain,service,{'entity_id':entity,**safe}))
            if path=='/api/assistant':
                cfg=read_settings()
                if not cfg['assistant']['enabled']:raise ValueError('Assistente disattivato')
                msg=str(data.get('text','')).strip()
                if not msg or len(msg)>1200:raise ValueError('Messaggio non valido')
                payload={'text':msg,'language':'it'}
                agent=cfg['assistant']['agent_id']
                if agent:payload['agent_id']=agent
                conversation=str(data.get('conversation_id',''))[:100]
                if conversation:payload['conversation_id']=conversation
                return self.respond(200,ha_request('POST','conversation/process',payload))
            if path=='/api/notification/test':
                cfg=read_settings();dom,service=cfg['notifications']['service'].split('.',1)
                return self.respond(200,call_service(dom,service,{'title':'AIDOS','message':'Notifica di prova da AIDOS'}))
            return self.respond(404,{'error':'Percorso inesistente'})
        except (ValueError,TypeError,KeyError) as e:self.respond(400,{'error':str(e)})
        except Exception as e:self.respond(502,{'error':str(e)})

    def log_message(self, fmt,*args):
        LOG.info('%s %s',self.address_string(),fmt%args)


def main():
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    DATA.mkdir(parents=True,exist_ok=True)
    threading.Thread(target=notification_loop,name='notifications',daemon=True).start()
    LOG.info('AIDOS in ascolto su %s:%s',HOST,PORT)
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()

if __name__=='__main__':main()
