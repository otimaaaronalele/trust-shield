export type TxType = "CASH_OUT" | "TRANSFER";

export interface TxPayload {
  step: number;
  type: TxType;
  amount: number;
  old_balance: number;
  nameOrig: string;
  oldbalanceOrg: number;
  newbalanceOrig: number;
  nameDest: string;
  oldbalanceDest: number;
  newbalanceDest: number;
}

export interface BackendResponse {
  action_routing: string;
  fraud_probability: number;
  system_latency_ms: number;
  plain_language_brief: string;
}

export type ReviewerDecision = "Pending" | "Approved" | "Escalated" | "Released";

export interface HistoryRecord {
  time: string;
  type: TxType;
  amount: number;
  old_balance: number;
  routing: string;
  fraud_probability: number;
  server_latency_ms: number;
  round_trip_ms: number;
  brief: string;
  reviewer_decision: ReviewerDecision;
  decided_at?: string;
  reviewer_note?: string;
}
