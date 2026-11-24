#!/usr/bin/env python3
from usage import scan
import argparse, collections, hashlib, json, pathlib, re, xml.etree.ElementTree as ET, difflib, subprocess
P=pathlib.Path
NS='{http://www.w3.org/2000/svg}'
def sha(b): return hashlib.sha256(b).hexdigest()
def inventory(root):
    out={}
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.suffix.lower()!='.svg': continue
        b=p.read_bytes(); s=b.decode('utf-8',errors='replace'); errors=[]; warnings=[]; geom=None; meta={}; unsafe=False
        try:
            if re.search(r'<!DOCTYPE|<!ENTITY',s,re.I): raise ValueError('DTD/entity declaration: excluded from XML parsing')
            e=ET.fromstring(b)
            if e.tag!=NS+'svg': errors.append('Root is not an SVG in the SVG namespace')
            ids=[x.get('id') for x in e.iter() if x.get('id')]; dup=[k for k,v in collections.Counter(ids).items() if v>1]
            if dup: errors.append('Duplicate IDs: '+', '.join(dup))
            vb=e.get('viewBox'); meta={k:e.get(k) for k in ('viewBox','width','height')}
            if vb:
                try:
                    import math
                    n=list(map(float,re.split(r'[\s,]+',vb.strip())))
                    if len(n)!=4 or not all(map(math.isfinite,n)) or min(n[2:])<=0: raise ValueError()
                except ValueError: errors.append('Invalid or non-positive viewBox')
            else: warnings.append('No viewBox; check scalability')
            colors=set(); refs=set(); unsafe=False
            def shape(x):
                nonlocal unsafe
                tag=x.tag.split('}')[-1]; attrs={}
                if tag in ('script','foreignObject','style','animate','set','animateTransform','animateMotion'): unsafe=True
                for k,v in x.attrib.items():
                    key=k.split('}')[-1]
                    if key.lower().startswith('on'): unsafe=True
                    if key in ('fill','stroke','color','stop-color'): colors.add(v)
                    if key=='href':
                        if v.startswith('#'): refs.add(v[1:])
                        else: unsafe=True
                    for ref in re.findall(r'url\(\s*[\"\']?#([^\s)\"\']+)',v): refs.add(ref)
                    if 'url(' in v and not re.search(r'url\(\s*[\"\']?#',v): unsafe=True
                    if key not in ('fill','stroke','color','stop-color','id','class'): attrs[k]=v
                return [x.tag,sorted(attrs.items()),[shape(c) for c in x]]
            geom=sha(json.dumps(shape(e),sort_keys=True).encode()); meta['colors']=sorted(colors)
            if refs-set(ids): errors.append('Unresolved IDs: '+', '.join(sorted(refs-set(ids))))
            tags={x.tag.split('}')[-1] for x in e.iter()}
            if not tags.intersection({'path','rect','circle','ellipse','line','polyline','polygon','text','image','use'}): warnings.append('No recognizable drawable element')
            for node in e.iter():
                tag=node.tag.split('}')[-1]
                if tag=='path':
                    d=node.get('d','').strip()
                    if not d: warnings.append('Empty path data')
                    elif not re.match(r'^[Mm]',d) or re.search(r'[^MmZzLlHhVvCcSsQqTtAaEe0-9.,+\-\s]',d): errors.append('Suspicious or invalid path data syntax')
                if tag in ('svg','rect','image','use'):
                    for dim in ('width','height'):
                        val=node.get(dim,'').strip()
                        if re.match(r'^-\d',val): errors.append('Negative '+dim+' on '+tag)
                if tag in ('title','desc') and not ''.join(node.itertext()).strip(): warnings.append('Empty '+tag+' metadata')
            if any(v not in ('none','currentColor','inherit','transparent') and not v.startswith('url(') for v in colors): warnings.append('Explicit paint values: check light, dark and forced-colours contexts')
            if unsafe: warnings.append('Active content, stylesheet or external reference: preview blocked pending inspection')
        except (ET.ParseError,ValueError) as ex: errors.append(str(ex)); unsafe=True
        rel=p.relative_to(root).as_posix(); out[rel]={'path':rel,'hash':sha(b),'geometry':geom,'bytes':len(b),'source':s,'errors':errors,'warnings':warnings,'meta':meta,'blocked':unsafe}
    return out

def build(a,b):
    rows=[]; used=set()
    for path,x in a.items():
        exact=[k for k,y in b.items() if x['hash']==y['hash']]
        similar=[k for k,y in b.items() if x['geometry'] and x['geometry']==y['geometry']]
        names=[k for k in b if P(k).name==P(path).name]
        candidates=list(dict.fromkeys(([path] if path in b else [])+exact+similar+names))
        target=candidates[0] if candidates else None
        if target: used.add(target)
        status='unresolved' if not target else 'unchanged' if path==target and path in exact else 'relocated' if target in exact else 'modified' if path==target else 'candidate replacement'
        rows.append({'before':path,'after':target,'candidates':candidates,'status':status})
    for path in b:
        if path not in used: rows.append({'before':None,'after':path,'candidates':[path],'status':'added / unmatched'})
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--before',default='before/core/themes/default_admin'); ap.add_argument('--after',default='after/core/themes/default_admin'); args=ap.parse_args()
    roots=[P(args.before),P(args.after)]
    if not all(p.is_dir() for p in roots): ap.error('Both source directories must exist')
    a,b=map(inventory,roots); rows=build(a,b)
    provenance={'before directory':str(roots[0]),'after directory':str(roots[1])}
    if P('drupal.git').is_dir():
        for ref in ('before','after'):
            proc=subprocess.run(['git','--git-dir=drupal.git','rev-parse','refs/heads/'+ref],capture_output=True,text=True)
            if proc.returncode==0: provenance[ref+' cached Git ref (export not independently verified)']=proc.stdout.strip()
    usage={'before':scan(roots[0],a),'after':scan(roots[1],b)}
    # Search the new tree for old paths too, to expose possible stale references.
    usage['oldPathsInAfter']=scan(roots[1],a)
    P('usage.json').write_text(json.dumps(usage,indent=2))
    for side,assets in [('before',a),('after',b)]:
        for path,z in assets.items(): z['usage']=usage[side]['hits'][path]
    data={'before':a,'after':b,'rows':rows,'provenance':provenance,'usage':usage}; raw=json.dumps(data,ensure_ascii=True).replace('<','\\u003c')
    template=P(__file__).with_name('template.html').read_text(); P('review.html').write_text(template.replace('/* DATA */',raw)); P('inventory.json').write_text(json.dumps(data,indent=2)); print(f'{len(a)} before, {len(b)} after, {len(rows)} review rows. Open review.html.')
if __name__=='__main__': main()
