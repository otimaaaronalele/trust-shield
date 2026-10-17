"""Batch faithfulness run over real packets.
Usage:  python run_batch.py [none|ollama|llama] [packets.jsonl] [limit]
  none   = no AI, fallback sentences only (checks the pipeline)
  ollama = Ollama on your PC (set OLLAMA_MODEL, default granite3.3:2b - confirm the name)
  llama  = llama-cpp-python on the server (set MODEL_PATH to the .gguf file)
"""
import os, sys, json, time, csv, statistics
from collections import Counter
from src.brief import generate_brief

def make_backend(name):
    if name == "none":
        return None
    if name == "ollama":
        import requests
        model = os.getenv("OLLAMA_MODEL", "granite3.3:2b")
        def fn(messages):
            r = requests.post("http://localhost:11434/v1/chat/completions", timeout=180,
                              json={"model": model, "messages": messages,
                                    "temperature": 0.0, "max_tokens": 150})
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        return fn
    if name == "llama":
        from llama_cpp import Llama
        llm = Llama(model_path=os.environ["MODEL_PATH"], n_ctx=2048, verbose=False)
        def fn(messages):
            out = llm.create_chat_completion(messages=messages, temperature=0.0, max_tokens=150)
            return out["choices"][0]["message"]["content"].strip()
        return fn
    raise SystemExit(f"unknown backend: {name}")

def run(slm_fn, path="eval/real_packets.jsonl", limit=None, out_csv="eval/faithfulness_results.csv"):
    packets = [json.loads(l) for l in open(path) if l.strip()]
    if limit:
        packets = packets[:limit]
    times, rows = [], []
    def timed(messages):
        t0 = time.perf_counter()
        try:
            return slm_fn(messages)
        finally:
            times.append(time.perf_counter() - t0)
    fn = timed if slm_fn else None
    for p in packets:
        out = generate_brief(p, slm_fn=fn)
        m = out["brief_meta"]
        rows.append({"id": p["transaction_id"], "decision": p["decision"], "source": m["source"],
                     "final_audit_passed": m["audit_passed"], "reasons": "; ".join(m["audit_reasons"]),
                     "brief": out["plain_language_brief"]})
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    n = len(rows)
    src = Counter(r["source"] for r in rows)
    print(f"packets run: {n}")
    print(f"  SLM accepted on first pass : {src['slm']/n:.1%}")
    print(f"  rescued by safe template   : {src['template_after_audit_fail']/n:.1%}")
    print(f"  SLM missing or errored     : {src['template_fallback']/n:.1%}")
    print(f"  final briefs passing audit : {sum(r['final_audit_passed'] for r in rows)/n:.1%}")
    for d in ("HOLD", "REVIEW", "RELEASE"):
        sub = [r for r in rows if r["decision"] == d]
        if sub:
            print(f"    {d:8s} first-pass: {sum(r['source']=='slm' for r in sub)/len(sub):.1%}  (n={len(sub)})")
    if times:
        print(f"  seconds per brief: median {statistics.median(times):.2f}, max {max(times):.2f}")
    why = Counter(x.split(":")[0] for r in rows for x in r["reasons"].split("; ") if x)
    if why:
        print("  most common rejection reasons:", dict(why.most_common(5)))
    print(f"  details saved to {out_csv}")
    return rows

if __name__ == "__main__":
    be = sys.argv[1] if len(sys.argv) > 1 else "none"
    path = sys.argv[2] if len(sys.argv) > 2 else "eval/real_packets.jsonl"
    lim = int(sys.argv[3]) if len(sys.argv) > 3 else None
    run(make_backend(be), path, lim)
