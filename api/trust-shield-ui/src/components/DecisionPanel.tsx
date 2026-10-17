import { useState, type ReactNode } from "react";
import type { HistoryRecord, ReviewerDecision } from "../types";
import Metric from "./Metric";

interface DecisionPanelProps {
  history: HistoryRecord[];
  onDecision: (choice: ReviewerDecision, note: string) => void;
}

export default function DecisionPanel({
  history,
  onDecision,
}: DecisionPanelProps) {
  const [note, setNote] = useState("");
  const last = history.length > 0 ? history[history.length - 1] : null;

  if (!last) {
    return (
      <div>
        <h3 className="subheader">Decision</h3>
        <div className="banner info">Run a system check to see the decision.</div>
      </div>
    );
  }

  const r = last.routing;
  let banner: ReactNode;
  if (r === "HARD_INTERCEPT_ESCROW" || r === "HOLD") {
    banner = <div className="banner error">🚨 HIGH RISK: transaction held</div>;
  } else if (r === "REVIEW") {
    banner = (
      <div className="banner warning">🔎 REVIEW: queued for a human reviewer</div>
    );
  } else if (r === "SETTLE_IMMEDIATELY" || r === "RELEASE") {
    banner = <div className="banner success">✅ LOW RISK: release</div>;
  } else {
    banner = <div className="banner info">Unrecognised routing value: {r}</div>;
  }

  const old = last.old_balance;
  const ratio = old > 0 ? last.amount / old : 0;
  const drain = old > 0 && Math.abs(last.amount - old) <= 1.0;

  return (
    <div>
      <h3 className="subheader">Decision</h3>
      {banner}
      <div className="row-3">
        <Metric
          label="Fraud probability"
          value={`${Math.round(last.fraud_probability * 100)}%`}
        />
        <Metric label="Server latency" value={`${last.server_latency_ms} ms`} />
        <Metric label="Round trip" value={`${last.round_trip_ms} ms`} />
      </div>
      <div className="field-group">
        <label className="field-label">Case file brief</label>
        <textarea readOnly value={last.brief} rows={4} />
      </div>

      <p><strong>Evidence from the transaction</strong></p>
      <div className="row-3">
        <Metric label="Amount / old balance" value={`${Math.round(ratio * 100)}%`} />
        <Metric label="Exceeds balance?" value={last.amount > old ? "Yes" : "No"} />
        <Metric label="Full-drain pattern" value={drain ? "Yes" : "No"} />
      </div>
      <p className="evidence-note">
        Evidence is computed from the entered values. The decision itself comes
        from the server.
      </p>

      <div className="field-group">
        <label className="field-label">Reviewer note (optional)</label>
        <input
          type="text"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
      </div>
      <p><strong>Reviewer action</strong></p>
      <div className="row-3">
        <button onClick={() => onDecision("Approved", note)}>✔ Approve</button>
        <button onClick={() => onDecision("Escalated", note)}>⚠ Escalate</button>
        <button onClick={() => onDecision("Released", note)}>🔓 Release</button>
      </div>
      <p className="decision-caption">
        Current decision: <strong>{last.reviewer_decision}</strong>
      </p>
    </div>
  );
}
