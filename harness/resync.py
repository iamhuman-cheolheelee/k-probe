"""Copy the current probe rules from probes.json into a results file (answers untouched)."""
import json,sys
P={r['id']:r for r in (lambda p:p if isinstance(p,list) else p['probes'])(json.load(open('probes.json')))}
for f in sys.argv[1:]:
    d=json.load(open(f))
    for r in d['results']:
        for k in ('pass','fail','first','note','src','sev','cat','pair','set'):
            if k in P.get(r['id'],{}): r[k]=P[r['id']][k]
    json.dump(d,open(f,'w'),ensure_ascii=False,indent=1)
