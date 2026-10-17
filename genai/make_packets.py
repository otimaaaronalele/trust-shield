"""Turns DS1's test_predictions.csv into packets in the v1.1 contract shape.
Usage: python make_packets.py test_predictions.csv model_meta.json
Assumption to confirm with DS1: amount_exceeds_balance means amount > oldbalanceOrg.
"""
import sys, json, os
import pandas as pd
from src.audit import audit_brief
from src.brief import template_brief

csv_path = sys.argv[1] if len(sys.argv) > 1 else "test_predictions.csv"
meta_path = sys.argv[2] if len(sys.argv) > 2 else "model_meta.json"
threshold = json.load(open(meta_path))["threshold"]
df = pd.read_csv(csv_path)

def to_packet(i, row):
    return {"transaction_id": f"TX-{i:06d}", "decision": row.decision,
            "score": round(float(row.score), 6), "threshold": round(threshold, 6),
            "rule_fired": bool(row.rule_fired),
            "evidence": {"type": row.type, "amount": round(float(row.amount), 2),
                         "oldbalanceOrg": round(float(row.oldbalanceOrg), 2),
                         "amount_to_old_balance": round(float(row.amount) / (float(row.oldbalanceOrg) + 1.0), 4),
                         "amount_exceeds_balance": bool(row.amount > row.oldbalanceOrg)}}

# 1) Does the fallback sentence pass the audit on EVERY real row?
bad = 0
for i, row in enumerate(df.itertuples(index=False)):
    ok, _ = audit_brief(template_brief(to_packet(i, row)), to_packet(i, row))
    bad += (not ok)
print(f"fallback brief passes audit on {len(df)-bad} of {len(df)} real rows")

# 2) Save 100 packets per decision for the batch run
os.makedirs("eval", exist_ok=True)
with open("eval/real_packets.jsonl", "w") as fh:
    out = []
    for dec in ("HOLD", "REVIEW", "RELEASE"):
        sub = df[df.decision == dec].sample(min(100, (df.decision == dec).sum()), random_state=1)
        out += [json.dumps(to_packet(i, row)) for i, row in zip(sub.index, sub.itertuples(index=False))]
    fh.write("\n".join(out))
print(f"saved {len(out)} packets to eval/real_packets.jsonl")
