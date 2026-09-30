"""Embed the three harness runs into demo/template.html -> demo/index.html (one static file, no server, no API key)."""
import json, base64, pathlib
h = pathlib.Path(__file__).resolve().parent; root = h.parent; H = root / 'harness'
RUNS = [('v15', 'Apertus 1.5 8B', 'results_v15_8b.json'), ('v15t', 'Apertus 1.5 8B + thinking', 'results_v15_8b_think.json'), ('v1', 'Apertus 1.0 8B (2509)', 'results_v1_8b.json')]
LINKS = {'pdf': 'https://link.chlee.dev/ek4t2b.pdf', 'video': 'https://link.chlee.dev/3yhcfyj8/kprobe-apertus-demo.mp4'}
runs = {}
for k, lab, f in RUNS:
    if (H / f).exists():
        d = json.load(open(H / f)); d['label'] = lab
        for r in d['results']: r.pop('raw', None)
        runs[k] = d
logo = 'data:image/png;base64,' + base64.b64encode((root / 'assets/hackapertus.png').read_bytes()).decode()
t = (h / 'template.html').read_text().replace('__LOGO__', logo).replace('__PDF__', LINKS['pdf']).replace('__VIDEO__', LINKS['video'])
t = t.replace('__DATA__',json.dumps({'primary':'v15','runs':runs},ensure_ascii=False).replace('</','<\\/'))
(h / 'index.html').write_text(t); print('wrote demo/index.html', len(t), 'bytes', list(runs))
