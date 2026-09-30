"""K-Probe runner: Korean red-team probes against Apertus (MLX local), greedy decoding.
Usage: python run.py [model] [--out results.json] [--think] [--only v2]
Apertus 1.5 exposes an optional thinking mode (chat template flag enable_thinking).
With --think the reasoning block (<think>...</think>) is kept in 'raw' and removed from 'answer' before scoring."""
import json, re, sys, time, pathlib, argparse
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
ap = argparse.ArgumentParser()
ap.add_argument("model", nargs="?", default="m1rkocasu/Apertus-v1.5-8B-text-MLX-8bit")
ap.add_argument("--out", default="results.json"); ap.add_argument("--think", action="store_true")
ap.add_argument("--only", default=""); ap.add_argument("--max", type=int, default=0)
a = ap.parse_args()
D = pathlib.Path(__file__).parent
probes = [p for p in json.load(open(D/"probes.json")) if not a.only or p.get("set") == a.only]
model, tok = load(a.model, tokenizer_config={"fix_mistral_regex": True})
samp = make_sampler(temp=0.0)
MAXT = a.max or (2400 if a.think else 400)
def hangul_ratio(s):
    L = [c for c in s if c.isalpha()]
    return round(sum('가' <= c <= '힣' for c in L)/max(1,len(L)), 2)
out = []
for p in probes:
    msgs = [{"role": "user", "content": p["q"]}]
    kw = {"enable_thinking": bool(a.think)}  # the 1.5 template defaults to thinking ON when the flag is absent
    prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, **kw)
    t = time.time(); raw = generate(model, tok, prompt=prompt, max_tokens=MAXT, sampler=samp).strip()
    ans = re.sub(r'^[\s\S]*?</think>', '', raw).strip() if '</think>' in raw else raw
    r = {**p, "answer": ans, "sec": round(time.time()-t, 1), "hangul": hangul_ratio(ans)}
    if raw != ans: r["raw"] = raw
    out.append(r)
    print(p["id"], r["sec"], ans[:90].replace("\n", " "), flush=True)
json.dump({"model": a.model, "date": time.strftime("%Y-%m-%d"), "temp": 0.0, "thinking": a.think, "max_tokens": MAXT, "results": out},
          open(D/a.out, "w"), ensure_ascii=False, indent=1)
