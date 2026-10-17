"""Trust-Shield evidence contract v1.1 (three outcomes). Hand this file to the SWE.
Needs: pip install pydantic   (FastAPI already installs it)
"""
from typing import Literal
from pydantic import BaseModel

class TransactionRequest(BaseModel):
    transaction_id: str
    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float

class Evidence(BaseModel):
    type: str                        # CASH_OUT or TRANSFER
    amount: float                    # 2 decimals
    oldbalanceOrg: float             # 2 decimals
    amount_to_old_balance: float     # 4 decimals; = amount / (oldbalanceOrg + 1.0)  (DS1's formula)
    amount_exceeds_balance: bool     # DS1's feature (assumed: amount > oldbalanceOrg)

class BriefMeta(BaseModel):
    source: Literal["slm", "template_fallback", "template_after_audit_fail"]
    audit_passed: bool               # did the FINAL brief pass the audit?
    audit_reasons: list[str]         # why the SLM draft was rejected (empty if accepted)

class VerifyResponse(BaseModel):
    contract_version: str = "1.1"
    transaction_id: str
    decision: Literal["HOLD", "REVIEW", "RELEASE"]
    score: float                     # model score, 6 decimals. NOT a probability.
    threshold: float                 # 6 decimals; the REAL threshold from model_meta.json
    rule_fired: bool                 # rule: oldbalanceOrg > 0 and abs(amount - oldbalanceOrg) <= 1.0
    evidence: Evidence
    plain_language_brief: str
    brief_meta: BriefMeta
    system_latency_ms: float         # 3 decimals
