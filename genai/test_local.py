"""Runs on your PC with NO data and NO model. Made-up packets, pretend AI."""
import json, os, random
from collections import Counter
from src.audit import audit_brief
from src.brief import generate_brief, template_brief

THRESHOLD = 0.004458

def make_response(rng, i, decision=None):
    decision = decision or rng.choice(["HOLD", "REVIEW", "RELEASE", "RELEASE"])
    old = round(rng.uniform(1000, 500000), 2)
    amount = old if decision == "HOLD" else round(rng.uniform(500, 900000), 2)
    score = {"HOLD": 1.0, "REVIEW": round(rng.uniform(0.0045, 1.0), 6),
             "RELEASE": round(rng.uniform(0.0019, 0.0023), 6)}[decision]
    return {"transaction_id": f"TX-{i:06d}", "decision": decision, "score": score,
            "threshold": THRESHOLD, "rule_fired": decision == "HOLD",
            "evidence": {"type": rng.choice(["CASH_OUT", "TRANSFER"]), "amount": amount,
                         "oldbalanceOrg": old,
                         "amount_to_old_balance": round(amount / (old + 1.0), 4),
                         "amount_exceeds_balance": amount > old}}

def make_fake_slm(rng):
    def fake(messages):
        f = json.loads(messages[1]["content"].split("\n", 1)[1].rsplit("\n\nWrite the brief.", 1)[0])
        if f["rule_fired"]:
            text = (f"This {f['type']} of {f['amount']:,.2f} equals the sender's full balance "
                    f"of {f['oldbalanceOrg']:,.2f}. Decision applied: {f['decision']}.")
        else:
            rel = "above" if f["decision"] == "REVIEW" else "below"
            text = (f"This {f['type']} of {f['amount']:,.2f} has a model score of {f['score']:.6f}, "
                    f"{rel} the threshold {f['threshold']:.6f}. Decision applied: {f['decision']}.")
        roll = rng.random()
        if roll < 0.10: text += " The sender had 7 prior alerts."
        elif roll < 0.18: text = text.replace(f["decision"], "BLOCK_NOW")
        elif roll < 0.23: text += " We recommend that this be blocked."
        elif roll < 0.28: text += " Score is 92% likely fraud."
        return text
    return fake

rng = random.Random(42)
print("PART 1: hand-checked cases")
for dec in ("HOLD", "REVIEW", "RELEASE"):
    r = make_response(rng, 123, dec)
    t = template_brief(r)
    for name, text in [("honest", t), ("invented number", t + " The sender had 5 alerts."),
                       ("decision language", t + " I recommend blocking it.")]:
        ok, why = audit_brief(text, r)
        print(f"  {dec:8s} {name:18s} -> {'ACCEPT' if ok else 'REJECT'} {why}")

print("\nPART 2: example fallback brief")
print(" ", template_brief(make_response(rng, 7, "REVIEW")))

print("\nPART 3: 300 made-up packets, pretend AI that sometimes lies")
fake, src = make_fake_slm(rng), Counter()
for i in range(300):
    src[generate_brief(make_response(rng, i), slm_fn=fake)["brief_meta"]["source"]] += 1
n = sum(src.values())
print(f"  first-pass faithfulness (SLM accepted): {src['slm']/n:.1%}")
print(f"  rescued by safe template:               {src['template_after_audit_fail']/n:.1%}")
