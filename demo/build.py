"""Embed harness/results.json into demo/template.html -> demo/index.html (one static file, no server)."""
import json, base64, pathlib
h = pathlib.Path(__file__).resolve().parent; root = h.parent
d = json.load(open(root / 'harness/results.json'))
logo = 'data:image/png;base64,' + base64.b64encode((root / 'assets/hackapertus.png').read_bytes()).decode()
t = (h / 'template.html').read_text().replace('__LOGO__', logo).replace('__DATE__', d['date']).replace('__DATA__', json.dumps(d, ensure_ascii=False).replace('</', '<\\/'))
(h / 'index.html').write_text(t); print('wrote demo/index.html', len(t), 'bytes')
