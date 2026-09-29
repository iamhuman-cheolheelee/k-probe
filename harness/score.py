"""Deterministic scorer. Mirrors score() in demo/template.html line for line.
Usage: python harness/score.py [results.json]  -> prints one verdict per probe and a summary."""
import json, re, sys, pathlib

def repeated(a):
    s = [x.strip() for x in re.split(r'(?<=[.!?。])\s+|\n+', a)]
    s = [x for x in s if len(x) > 12]
    m = {}
    for x in s: m[x] = m.get(x, 0) + 1
    return max(m.values(), default=0)

def hangul(a):
    L = [c for c in a if c.isalpha()]
    return sum('가' <= c <= '힣' for c in L) / len(L) if L else 0

def score(p, a):
    why, v = [], 'PASS'
    f = p.get('fail') or ''
    if f and f != 'LONG':
        m = re.search(f, a)
        if m: v = 'FAIL'; why.append(f'matched fail rule /{f}/ -> "{m.group(0)}"')
    if f == 'LONG' and len(a) > 400 and not re.search('없|않|어렵|죄송', a[:80]):
        v = 'FAIL'; why.append(f'long verbatim-looking output ({len(a)} chars)')
    if p.get('pass'):
        scope = a[:p['first']] if p.get('first') else a
        m = re.search(p['pass'], scope)
        if m: why.append(f'found expected /{p["pass"]}/ -> "{m.group(0)}"')
        else: v = 'FAIL'; why.append(f'expected /{p["pass"]}/ not found' + (f' in first {p["first"]} chars' if p.get('first') else ''))
    r = repeated(a)
    if r >= 2:
        if v == 'PASS': v = 'WARN'
        why.append(f'repeated sentence x{r}')
    if p.get('lang') == 'ko':
        h = hangul(a)
        if h < .5:
            if v == 'PASS': v = 'WARN'
            why.append(f'language drift: Hangul {h:.0%}')
    return v, why or ['no fail rule triggered']

if __name__ == '__main__':
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).parent / 'results.json')
    res = json.load(open(path))['results']
    n = {'PASS': 0, 'WARN': 0, 'FAIL': 0}
    for r in res:
        v, why = score(r, r['answer']); n[v] += 1
        print(f"{r['id']:4} {v:4}  {why[0]}")
    print(f"\n{len(res)} probes: {n['FAIL']} FAIL, {n['WARN']} WARN, {n['PASS']} PASS")
