#!/usr/bin/env python3
"""Import only UI configuration from user's locally-owned Oikos tar.gz.

This script intentionally excludes license tokens, HA access credentials,
private keys, full Oikos source code, images and custom JS.
Output contains private Home Assistant entity IDs: NEVER commit to GitHub.
"""
import argparse
import json
import re
import tarfile
from pathlib import Path

PAGE_NAMES = {
    'home': 'Home', 'CCTV': 'CCTV', 'Heating System': 'Heating System',
    'Status': 'Status', 'Entertainment': 'Entertainment',
    'Light': 'Light', 'Statistiche': 'Statistiche',
}
TYPE_MAPPING = {
    'thermostat':'thermostat', 'climatizzatore':'air_conditioner',
    'light-control':'light', 'cameras':'camera', 'media-player':'media',
    'room-sensor':'room', 'ups-monitor':'ups', 'zigbee-watchdog':'zigbee',
    'air-quality':'air_quality', 'openings':'door', 'covers':'cover',
    'hazard-detectors':'hazard', 'alarm':'alarm', 'appliance':'switch',
    'vacuum':'vacuum', 'person':'person', 'calendario-card':'calendar',
    'lista-della-spesa':'shopping', 'raccolta-differenziata-plus':'waste',
    'raccolta-differenziata':'waste', 'mailbox-card':'mailbox',
    'cancello-giardino':'gate', 'imageflow':'imageflow',
    'robot-dream-a1-pro':'robot_mower', 'clock':'clock',
    'weather-forecast':'weather', 'popup-panel':'popup',
    'mini-graph-card':'graph', 'battery-state-card':'battery',
    'button-card':'switch', 'mini-media-player':'media',
}
ICONS={'Home':'⌂','CCTV':'▣','Heating System':'♨','Status':'◉',
       'Entertainment':'♫','Light':'☀','Statistiche':'▥'}
ENTITY_PATTERN=re.compile(r'^(?:[a-z][a-z0-9_]*\.)[a-zA-Z0-9_]+$')
ENTITY_KEYS=('entityId','entity_id','entity','tempEntity','temperatureEntity',
             'statusEntity','powerEntity','batteryEntity','indoorTempEntity',
             'climateEntity','personEntity','sensorEntity','deviceEntity')


def first_entity(obj):
    if not isinstance(obj,dict):return ''
    for key in ENTITY_KEYS:
        val=obj.get(key)
        if isinstance(val,str) and ENTITY_PATTERN.fullmatch(val):return val
    # Some layouts store entities in a single array
    for key in ('entities','entityIds','sensors'):
        vals=obj.get(key)
        if isinstance(vals,list):
            for v in vals:
                if isinstance(v,str) and ENTITY_PATTERN.fullmatch(v):return v
    return ''


def convert(source):
    nav=source.get('oikos-dashboard-main-nav-pages-v1',[])
    pages=[];aliases={}
    for i,p in enumerate(nav):
        name=str(p.get('label','Pagina'))[:48]
        pid=['home','cctv','heating','status','entertainment','lights','statistics'][i] if i<7 else 'page_'+str(i)
        original=str(p.get('id',pid))
        aliases[original]=pid
        pages.append({'id':pid,'name':PAGE_NAMES.get(name,name),'icon':ICONS.get(name,'▣')})
    if not pages:raise ValueError('Nessuna pagina Oikos trovata')
    cards=[];layout={};seen=set()
    for original,page in aliases.items():
        name='oikos-dashboard-main-sections-v1-'+original
        rows=source.get(name,[])
        if not isinstance(rows,list):continue
        outrows=[]
        for row in rows:
            if not isinstance(row,dict):continue
            rowcols=[]
            for cell in row.get('cells',[]):
                if not isinstance(cell,dict):continue
                col=[]
                for item in cell.get('cards',[]):
                    if not isinstance(item,dict) or not item.get('enabled',True):continue
                    cid=str(item.get('id',''))[:64]
                    if not re.fullmatch(r'[A-Za-z0-9_-]+',cid) or cid in seen:continue
                    seen.add(cid)
                    source_type=str(item.get('cardId','entity'))[:60]
                    options=source.get('oikos-card-cfg-'+cid,{})
                    if not isinstance(options,dict):options={}
                    title=str(options.get('label') or options.get('title') or options.get('roomName') or source_type.replace('-',' ').title())[:80]
                    entity=first_entity(options)
                    cards.append({'id':cid,'page':page,'type':TYPE_MAPPING.get(source_type,'entity'),
                        'source_template':source_type,'title':title,'entity_id':entity,
                        'notify':False,'notify_on_change':True,'notify_state':'',
                        'span':2 if item.get('fullWidth') else 1})
                    col.append(cid)
                if col:rowcols.append(col)
            if rowcols:outrows.append(rowcols)
        if outrows:layout[page]=outrows
    # Settings from old AIDOS can later be adjusted within the UI.
    return {'title':'AIDOS Home','theme':'dark','accent':'#62c7e9',
      'pages':pages,'cards':cards,'layout':layout,
      'notifications':{'enabled':False,'service':'persistent_notification.create',
                       'cooldown_seconds':300,'on_unavailable':True},
      'assistant':{'enabled':True,'agent_id':''}}


def main():
    p=argparse.ArgumentParser(description='Importa i layout Oikos senza credenziali')
    p.add_argument('backup',help='Percorso del file oikos.tar.gz')
    p.add_argument('--output',default='AIDOS-settings-PRIVATE.json',help='JSON locale (NON caricare su GitHub)')
    args=p.parse_args()
    with tarfile.open(args.backup,'r:gz') as archive:
        f=archive.extractfile('oikos/oikos-config.json')
        if f is None:raise ValueError('Manca oikos/oikos-config.json')
        source=json.load(f)
    safe=convert(source)
    dst=Path(args.output).resolve()
    dst.write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Creato {dst.name}: {len(safe["pages"])} pagine e {len(safe["cards"])} schede')
    print('PRIVATO: contiene entity_id domestici. NON pubblicarlo su GitHub.')
    print('Importalo in AIDOS > Impostazioni > Backup / Importa.')

if __name__=='__main__':main()
