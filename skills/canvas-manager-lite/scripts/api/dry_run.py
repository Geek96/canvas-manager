"""Dry run: compare prepared objects with the manifest by content hash.
usage: dry_run.py <data-dir> <outdir-for-course>"""
import json,sys,hashlib
from pathlib import Path
dd=Path(sys.argv[1]); out=Path(sys.argv[2])
m=json.loads((dd/'raw/_manifest/canvas-objects.json').read_text())
for f in sorted(out.glob('*.json')):
    t=f.stem; objs=json.loads(f.read_text())
    ch=[];new=[]
    for o in objs:
        k=f"{t}/{o['canvas_id']}"; h=hashlib.sha256(o['content'].encode()).hexdigest()
        if k not in m: new.append(k+' '+o['title'][:50])
        elif m[k].get('content_hash')!=h: ch.append(k+' '+o['title'][:50])
    seen={f"{t}/{o['canvas_id']}" for o in objs}
    miss=[k for k,v in m.items() if k.startswith(t+'/') and k not in seen and v.get('status')=='active']
    print(t,'n',len(objs),'new',len(new),'changed',len(ch),'missing',miss); [print('   +',c) for c in new[:20]]; [print('   ~',c) for c in ch[:20]]
