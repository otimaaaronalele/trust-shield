"""Brief generation: SLM draft -> audit -> safe template if anything is off."""
import json
from src.audit import audit_brief

SYSTEM_PROMPT = (
    "You are a fraud-operations assistant. Write a 2-3 sentence case brief for a "
    "human reviewer using ONLY the facts in the JSON evidence provided. Rules: copy "
    "numbers exactly as given; do not compute new numbers; do not invent facts; do "
    "not decide, approve, block, or recommend an action. If rule_fired is true, say "
    "the amount matched the sender's full balance. If amount_exceeds_balance is true, "
    "say the amount exceeded the sender's balance and do not describe "
    "amount_to_old_balance as a share. 'score' is a model score, not a probability. "
    "End by stating the decision label that was already applied, written exactly as given."
)

def build_facts(r: dict) -> dict:
    e = r["evidence"]
    return {"type": e["type"], "amount": e["amount"], "oldbalanceOrg": e["oldbalanceOrg"],
            "amount_to_old_balance": e["amount_to_old_balance"],
            "amount_exceeds_balance": e["amount_exceeds_balance"],
            "rule_fired": r["rule_fired"], "score": r["score"],
            "threshold": r["threshold"], "decision": r["decision"]}

def build_messages(r: dict) -> list:
    return [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Evidence JSON:\n{json.dumps(build_facts(r))}\n\nWrite the brief."}]

def template_brief(r: dict) -> str:
    """Deterministic fallback. Faithful by construction."""
    e, d = r["evidence"], r["decision"]
    head = f"Transaction {r['transaction_id']} ({e['type']}, amount {e['amount']:.2f})"
    if r["rule_fired"]:
        body = f"matched the hold rule: the amount equals the sender's full balance of {e['oldbalanceOrg']:.2f}."
    else:
        rel = "at or above" if d == "REVIEW" else "below"
        body = (f"did not match the hold rule. The model score {r['score']:.6f} is {rel} "
                f"the review threshold {r['threshold']:.6f}.")
        if e["amount_exceeds_balance"]:
            body += f" The amount exceeds the sender's balance of {e['oldbalanceOrg']:.2f}."
    tail = {"HOLD": "Decision applied: HOLD.",
            "REVIEW": "Decision applied: REVIEW (queued for human review).",
            "RELEASE": "Decision applied: RELEASE."}[d]
    return f"{head} {body} {tail}"

def generate_brief(r: dict, slm_fn=None) -> dict:
    """slm_fn: function taking chat messages, returning text. None -> fallback only."""
    draft_reasons, source, text = [], "template_fallback", None
    if slm_fn is not None:
        try:
            draft = slm_fn(build_messages(r))
            ok, draft_reasons = audit_brief(draft, r)
            if ok:
                text, source = draft, "slm"
            else:
                source = "template_after_audit_fail"
        except Exception as exc:
            draft_reasons, source = [f"slm error: {exc}"], "template_fallback"
    if text is None:
        text = template_brief(r)
    final_ok, _ = audit_brief(text, r)
    return {"plain_language_brief": text,
            "brief_meta": {"source": source, "audit_passed": final_ok,
                           "audit_reasons": draft_reasons}}
