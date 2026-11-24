"""Conservative literal source-reference discovery; not a proof of non-use."""
import collections, pathlib, re
P=pathlib.Path
EXT={'.css','.scss','.js','.mjs','.ts','.twig','.php','.module','.inc','.install','.yml','.yaml','.json','.html','.md','.txt','.pcss','.theme','.xml'}
PAT=re.compile(r"[\w./%+@~-]+\.svg(?:\?[^\s'\";)#]+)?",re.I)
def scan(root, paths):
    root=P(root); names=collections.defaultdict(list)
    for p in paths: names[P(p).name.lower()].append(p)
    hits={p:[] for p in paths}; unresolved=[]; scanned=0
    for f in sorted(root.rglob('*')):
        if not f.is_file() or f.suffix.lower() not in EXT or any(x in {'.git','node_modules','vendor'} for x in f.relative_to(root).parts): continue
        try: lines=f.read_text(errors='replace').splitlines()
        except OSError: continue
        scanned+=1
        for n,line in enumerate(lines,1):
            for m in PAT.finditer(line):
                raw=m.group(); token=raw.split('?')[0]; candidates=names.get(P(token).name.lower(),[])
                # Prefer a resolved path or suffix, not just basename.
                resolved=(f.parent/token).resolve()
                exact=[p for p in candidates if resolved==(root/p).resolve() or token.lstrip('/').endswith(p)]
                for p in exact or candidates:
                    hits[p].append({'file':f.relative_to(root).as_posix(),'line':n,'reference':raw,'match':'path' if exact else 'basename candidate','context':line.strip()[:400]})
                if not candidates and 'images/' in token: unresolved.append({'file':f.relative_to(root).as_posix(),'line':n,'reference':raw})
    return {'root':str(root),'filesScanned':scanned,'hits':hits,'unmatchedImageReferences':unresolved,'limitations':'Literal SVG references only; dynamic paths, aliases, generated code and references outside scope need separate inspection. Unmatched references are not confirmed broken links.'}
