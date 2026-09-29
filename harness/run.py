"""K-Probe runner: Korean red-team probes against Apertus (MLX local). Usage: python run.py [model]"""
import json, re, sys, time, pathlib
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
M = sys.argv[1] if len(sys.argv) > 1 else "mlx-community/Apertus-8B-Instruct-2509-4bit"
D = pathlib.Path(__file__).parent
probes = json.load(open(D/"probes.json"))
model, tok = load(M)
samp = make_sampler(temp=0.0)
def hangul_ratio(s):
    L = [c for c in s if c.isalpha()]
    return round(sum('가' <= c <= '힣' for c in L)/max(1,len(L)), 2)
out = []
for p in probes:
    msgs = [{"role": "user", "content": p["q"]}]
    prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
    t = time.time(); a = generate(model, tok, prompt=prompt, max_tokens=320, sampler=samp).strip()
    out.append({**p, "answer": a, "sec": round(time.time()-t, 1), "hangul": hangul_ratio(a)})
    print(p["id"], out[-1]["sec"], a[:90].replace("\n", " "), flush=True)
json.dump({"model": M, "date": time.strftime("%Y-%m-%d"), "temp": 0.0, "results": out}, open(D/"results.json", "w"), ensure_ascii=False, indent=1)
