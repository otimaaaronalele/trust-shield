import time
import requests
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Trust-Shield", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
div[data-testid="stMetric"] {background:#141C2E; padding:12px 16px;
border-radius:10px; border:1px solid #243049;}
</style>
""", unsafe_allow_html=True)
st.sidebar.header("⚙️ System settings")
USE_MOCK = st.sidebar.toggle("Mock mode (no backend)", value=True)
API_URL = st.sidebar.text_input("API URL", "http://127.0.0.1:8000/api/v1/verify-transaction")
if st.sidebar.button("Test connection"):
    try:
        base = API_URL.split("/api/")[0]
        requests.get(base + "/docs", timeout=3)
        st.sidebar.success("Server reachable")
    except Exception:
        st.sidebar.error("Cannot reach server")
st.sidebar.caption("Switch mock mode off once the SWE's server is running.")
st.title("🛡️ Trust-Shield: Risk Operations Console")
st.caption("Real-time transaction screening with human review")
if USE_MOCK:
    st.warning("🧪 DEMO MODE: results are simulated and do not come from the fraud model.")
else:
    st.success("🟢 LIVE: connected to the Trust-Shield model server.")

if "history" not in st.session_state:
    st.session_state["history"] = []
hist = st.session_state.get("history", [])
k1, k2, k3, k4 = st.columns(4)
k1.metric("Checks run", len(hist))
k2.metric("Intercepted", sum(h["routing"] == "HARD_INTERCEPT_ESCROW" for h in hist))
k3.metric("Settled", sum(h["routing"] == "SETTLE_IMMEDIATELY" for h in hist))
k4.metric("Avg round trip", f"{sum(h['round_trip_ms'] for h in hist)/len(hist):.1f} ms" if hist else "n/a")
st.divider()

def call_backend(payload):
    if USE_MOCK:
        old = payload["oldbalanceOrg"]
        ratio = payload["amount"] / old if old > 0 else 0
        flagged = ratio > 0.98
        return {
            "action_routing": "HARD_INTERCEPT_ESCROW" if flagged else "SETTLE_IMMEDIATELY",
            "fraud_probability": 0.92 if flagged else 0.04,
            "system_latency_ms": 0.0,
            "plain_language_brief": "MOCK RESPONSE: replace with the real backend.",
             }
    r = requests.post(API_URL, json=payload, timeout=5)
    r.raise_for_status()
    return r.json()

def set_decision(choice):
    if st.session_state["history"]:
        rec = st.session_state["history"][-1]
        rec["reviewer_decision"] = choice
        rec["decided_at"] = datetime.now().strftime("%H:%M:%S")
        rec["reviewer_note"] = st.session_state.get("note", "")

def preset_normal():
    st.session_state["amount"] = 5000.0
    st.session_state["old_bal"] = 150000.0

def preset_drain():
    st.session_state["amount"] = 150000.0
    st.session_state["old_bal"] = 150000.0

left, right = st.columns([1, 1.2], gap="large")

with left:
    st.subheader("Transaction")
    tx_type = st.selectbox("Type", ["CASH_OUT", "TRANSFER"])
    p1, p2 = st.columns(2)
    p1.button("Normal cash-out", on_click=preset_normal, use_container_width=True)
    p2.button("Full wallet drain", on_click=preset_drain, use_container_width=True)
    amount = st.number_input("Amount", value=150000.0, min_value=0.0, key="amount")
    old_bal = st.number_input("Sender old balance", value=150000.0, min_value=0.0, key="old_bal")
    if amount > old_bal:
        st.warning("Amount exceeds the sender's balance, so this transaction is inconsistent.")
    with st.expander("Advanced fields"):
        name_orig = st.text_input("Sender ID", "C01")
        name_dest = st.text_input("Recipient ID", "M01")
        old_dest = st.number_input("Recipient old balance", value=0.0, min_value=0.0)

    if st.button("🔍 Trigger System Check", type="primary", use_container_width=True):
        payload = {
            "step": 1, "type": tx_type, "amount": amount,"old_balance": old_bal,
            "nameOrig": name_orig, "oldbalanceOrg": old_bal,
            "newbalanceOrig": old_bal - amount,
            "nameDest": name_dest, "oldbalanceDest": old_dest,
            "newbalanceDest": old_dest + amount,
        }
        try:
            t0 = time.perf_counter()
            res = call_backend(payload)
            rtt = (time.perf_counter() - t0) * 1000
            st.session_state["history"].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": tx_type, "amount": amount,
                "old_balance": old_bal,
                "routing": res["action_routing"],
                "fraud_probability": res["fraud_probability"],
                "server_latency_ms": res["system_latency_ms"],
                "round_trip_ms": round(rtt, 2),
                "brief": res["plain_language_brief"],
                "reviewer_decision": "Pending",
            })
            st.rerun()
        except Exception as e:
            st.error(f"Backend disconnected: {e}")

with right:
    st.subheader("Decision")
    if st.session_state["history"]:
        last = st.session_state["history"][-1]
        r = last["routing"]
        if r in ("HARD_INTERCEPT_ESCROW", "HOLD"):
            st.error("🚨 HIGH RISK: transaction held")
        elif r == "REVIEW":
            st.warning("🔎 REVIEW: queued for a human reviewer")
        elif r in ("SETTLE_IMMEDIATELY", "RELEASE"):
            st.success("✅ LOW RISK: release")
        else:
            st.info(f"Unrecognised routing value: {r}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Fraud probability", f"{last['fraud_probability']:.0%}")
        m2.metric("Server latency", f"{last['server_latency_ms']} ms")
        m3.metric("Round trip", f"{last['round_trip_ms']} ms")
        st.text_area("Case file brief", last["brief"], height=120)

        old = last["old_balance"]
        ratio = last["amount"] / old if old > 0 else 0
        drain = old > 0 and abs(last["amount"] - old) <= 1.0
        st.write("**Evidence from the transaction**")
        e1, e2, e3 = st.columns(3)
        e1.metric("Amount / old balance", f"{ratio:.0%}")
        e2.metric("Exceeds balance?", "Yes" if last["amount"] > old else "No")
        e3.metric("Full-drain pattern", "Yes" if drain else "No")
        st.caption("Evidence is computed from the entered values. The decision itself comes from the server.")

        st.text_input("Reviewer note (optional)", key="note")
        st.write("**Reviewer action**")
        b1, b2, b3 = st.columns(3)
        b1.button("✔ Approve", on_click=set_decision, args=("Approved",), use_container_width=True)
        b2.button("⚠ Escalate", on_click=set_decision, args=("Escalated",), use_container_width=True)
        b3.button("🔓 Release", on_click=set_decision, args=("Released",), use_container_width=True)
        st.caption(f"Current decision: **{last['reviewer_decision']}**")
    else:
        st.info("Run a system check to see the decision.")

st.divider()
t1, t2, t3 = st.tabs(["📋 Case log", "📈 Latency", "🧠 About the model"])
hist_now = st.session_state["history"]

with t1:
    if hist_now:
        st.dataframe(pd.DataFrame(hist_now), use_container_width=True)
    else:
        st.info("No checks run yet.")
with t2:
    if hist_now:
        st.line_chart(pd.DataFrame(hist_now)["round_trip_ms"])
    else:
        st.info("No checks run yet.")

with t3:
    st.subheader("How the system decides")
    st.markdown(
        "1. **Rule:** amount equals the sender's balance (full drain) → **HOLD**\n"
        "2. **Model:** otherwise, a LightGBM score at or above the threshold → **REVIEW** by a human\n"
        "3. **Otherwise** → **RELEASE**\n\n"
        "The model uses only fields known before approval: type, amount, sender balance, recipient balance."
    )
    st.subheader("Test-set results")
    st.caption("PaySim synthetic data, time-based split, test set scored once. Source: DS1 notebook.")
    a, b, c, d = st.columns(4)
    a.metric("Recall", "1.000")
    b.metric("Precision", "0.885")
    c.metric("False-positive rate", "0.43%")
    d.metric("F1", "0.939")
    st.write("**What each layer contributes (test set, 51,286 transactions, 1,654 fraud)**")
    st.dataframe(pd.DataFrame({
        "Layer": ["Tier 1: rule (auto-hold)", "Tier 2: model only (human review)", "Combined"],
        "Flagged": [1596, 273, 1869],
        "True fraud": [1596, 58, 1654],
        "Honest customers held": [0, 215, 215],
        "Precision": [1.000, 0.2125, 0.885],
    }), use_container_width=True, hide_index=True)
    st.warning(
        "Limitations: PaySim is synthetic and its fraud patterns are simple, so these figures do not "
        "represent real-world performance. The rule's perfect precision reflects how PaySim generates fraud. "
        "The test set has a 3.2% fraud rate (training: 0.20%), so precision will differ elsewhere. "
        "Results come from a replay of completed records."
    )