"""Faithfulness audit: every number, the decision label, and 'no decisions by the AI'."""
import re

NUM_RE = re.compile(r"\d[\d,]*\.?\d*")
LABELS = ("HOLD", "REVIEW", "RELEASE")
FORBIDDEN = re.compile(
    r"\b(approve[ds]?|decline[ds]?|reject(ed)?|recommend\w*|"
    r"should (be )?(block|blocked|freeze|frozen|release|released|hold|held)|"
    r"must (block|freeze|release|hold))\b", re.I)

def fact_values(r: dict):
    """Returns (plain facts, percent versions of the ratio)."""
    e = r["evidence"]
    plain = [e["amount"], e["oldbalanceOrg"], e["amount_to_old_balance"],
             r["score"], r["threshold"]]
    pct = [] if e["amount_exceeds_balance"] else [e["amount_to_old_balance"] * 100]
    return [float(v) for v in plain], [float(v) for v in pct]

def number_ok(token: str, plain: list, pct: list, id_digits: set) -> bool:
    t = token.replace(",", "").rstrip(".")
    v = float(t)
    if v in id_digits:
        return True
    d = len(t.split(".")[1]) if "." in t else 0
    # Short numbers (0-1 decimals) must match a fact EXACTLY, so a stray "5" can't
    # sneak through by rounding a 4.6. Longer numbers may match a properly rounded fact.
    if any(abs(f - v) < 1e-9 for f in plain):
        return True
    if d >= 2 and any(round(f, d) == round(v, d) for f in plain):
        return True
    return any(round(f, d) == round(v, d) for f in pct)   # "100%"

def audit_brief(text: str, r: dict):
    reasons = []
    plain, pct = fact_values(r)
    id_digits = {float(x) for x in re.findall(r"\d+", str(r.get("transaction_id", "")))}
    for raw in NUM_RE.findall(text):
        if not number_ok(raw, plain, pct, id_digits):
            reasons.append(f"unsupported number: {raw}")
    if FORBIDDEN.search(text):
        reasons.append("decision language detected")
    dec = r["decision"]
    if not re.search(rf"\b{dec}\b", text):
        reasons.append("decision label missing")
    for other in LABELS:
        if other != dec and re.search(rf"\b{other}\b", text):
            reasons.append(f"wrong decision label mentioned: {other}")
    return (len(reasons) == 0), reasons
