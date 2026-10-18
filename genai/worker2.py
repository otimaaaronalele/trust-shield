"""DS2 brief worker for SWE's case queue.
SWE's API pushes each held case id to Redis list 'case_queue'. This worker pops it, builds the
brief with the audited DS2 layer, and writes brief / brief_validated / validator_outcome
into the 'cases' table. It never changes the decision.

Run from the genai folder:  PYTHONPATH=. python3 worker.py
Env (same names as the docker-compose genai-worker service): REDIS_HOST, REDIS_PORT, REDIS_CASE_QUEUE,
POSTGRES_*, SLM_MODEL_PATH (Granite .gguf, optional), SLM_TEMPERATURE, SLM_MAX_TOKENS
"""
import os, logging
from src.brief import generate_brief

log = logging.getLogger("ds2-worker")
ROUTE_TO_DECISION = {"HARD_INTERCEPT_ESCROW": "HOLD", "REVIEW": "REVIEW", "SETTLE_IMMEDIATELY": "RELEASE"}

def build_packet(transaction_id, action_routing, score, threshold, rule_fired, tx_type, amount, old_balance):
    """Maps SWE's fields to the DS2 evidence packet. SWE can also call this inside decide()
    to get an audited brief on the synchronous path."""
    amount, old_balance = float(amount), float(old_balance)
    return {"transaction_id": str(transaction_id)[:8],  # short id keeps digits out of the audit allowance
            "decision": ROUTE_TO_DECISION[action_routing],
            "score": round(float(score), 6), "threshold": round(float(threshold), 6),
            "rule_fired": bool(rule_fired),
            "evidence": {"type": tx_type, "amount": round(amount, 2),
                         "oldbalanceOrg": round(old_balance, 2),
                         "amount_to_old_balance": round(amount / (old_balance + 1.0), 4),
                         "amount_exceeds_balance": amount > old_balance}}

def packet_from_case(case_id, evidence_packet):
    tx, sc = evidence_packet["transaction"], evidence_packet["scoring"]
    return build_packet(case_id, evidence_packet["decision"], sc["score"], sc["threshold"],
                        sc["rule_fired"], tx["type"], tx["amount"], tx["old_balance_org"])

def process_case(cur, case_id, slm_fn=None):
    cur.execute("SELECT evidence_packet FROM cases WHERE case_id = %s", (case_id,))
    row = cur.fetchone()
    if row is None:
        log.warning("case %s not found", case_id); return None
    out = generate_brief(packet_from_case(case_id, row[0]), slm_fn=slm_fn)
    meta = out["brief_meta"]
    cur.execute("UPDATE cases SET brief = %s, brief_validated = %s, validator_outcome = %s WHERE case_id = %s",
                (out["plain_language_brief"], meta["audit_passed"], meta["source"], case_id))
    return meta["source"]

def load_slm():
    path = os.getenv("SLM_MODEL_PATH") or os.getenv("MODEL_GGUF")
    if not path or not os.path.exists(path):
        log.warning("No Granite model file at %r: using audited fallback briefs only", path); return None
    try:
        from llama_cpp import Llama
    except ImportError:
        log.warning("llama_cpp not installed: using audited fallback briefs only"); return None
    llm = Llama(model_path=path, n_ctx=2048, verbose=False)
    temp = float(os.getenv("SLM_TEMPERATURE", "0.0"))
    max_tokens = int(os.getenv("SLM_MAX_TOKENS", "150"))
    def fn(messages):
        o = llm.create_chat_completion(messages=messages, temperature=temp, max_tokens=max_tokens)
        return o["choices"][0]["message"]["content"].strip()
    return fn

def connect_with_retry(make, what):
    import time
    for attempt in range(40):
        try:
            return make()
        except Exception as exc:
            log.warning("waiting for %s (%s)", what, exc); time.sleep(3)
    raise SystemExit(f"could not reach {what}")

def main():
    import redis, psycopg2
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    queue = os.getenv("REDIS_CASE_QUEUE", "case_queue")
    def mk_redis():
        r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=int(os.getenv("REDIS_PORT", 6379)), decode_responses=True)
        r.ping(); return r
    r = connect_with_retry(mk_redis, "redis")
    cfg = dict(host=os.getenv("POSTGRES_HOST", "postgres"), port=int(os.getenv("POSTGRES_PORT", 5432)),
               database=os.getenv("POSTGRES_DB", "trustshield"), user=os.getenv("POSTGRES_USER", "admin"),
               password=os.getenv("POSTGRES_PASSWORD", "change_me"))
    connect_with_retry(lambda: psycopg2.connect(**cfg).close(), "postgres")
    slm = load_slm()
    log.info("worker ready, listening on %s", queue)
    while True:
        item = r.blpop(queue, timeout=5)
        if not item:
            continue
        case_id = item[1]
        conn = psycopg2.connect(**cfg)
        try:
            cur = conn.cursor()
            log.info("case %s -> %s", case_id, process_case(cur, case_id, slm))
            conn.commit()
        except Exception:
            conn.rollback(); log.exception("case %s failed", case_id)
        finally:
            conn.close()

if __name__ == "__main__":
    main()
