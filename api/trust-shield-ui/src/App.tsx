import { useState } from "react";
import type { HistoryRecord, ReviewerDecision, TxPayload } from "./types";
import { callBackend } from "./api";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import MetricsRow from "./components/MetricsRow";
import TransactionForm from "./components/TransactionForm";
import DecisionPanel from "./components/DecisionPanel";
import CaseLogTable from "./components/CaseLogTable";
import LatencyChart from "./components/LatencyChart";
import AboutTab from "./components/AboutTab";
import Tabs from "./components/Tabs";

export default function App() {
  const [useMock, setUseMock] = useState(true);
  const [apiUrl, setApiUrl] = useState(
    "http://127.0.0.1:8000/api/v1/verify-transaction"
  );
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (fields: {
    txType: "CASH_OUT" | "TRANSFER";
    amount: number;
    oldBal: number;
    nameOrig: string;
    nameDest: string;
    oldDest: number;
  }) => {
    const { txType, amount, oldBal, nameOrig, nameDest, oldDest } = fields;
    const payload: TxPayload = {
      step: 1,
      type: txType,
      amount,
      old_balance: oldBal,
      nameOrig,
      oldbalanceOrg: oldBal,
      newbalanceOrig: oldBal - amount,
      nameDest,
      oldbalanceDest: oldDest,
      newbalanceDest: oldDest + amount,
    };

    setSubmitting(true);
    setError(null);
    const t0 = performance.now();
    try {
      const res = await callBackend(payload, useMock, apiUrl);
      const rtt = performance.now() - t0;
      const record: HistoryRecord = {
        time: new Date().toLocaleTimeString("en-GB"),
        type: txType,
        amount,
        old_balance: oldBal,
        routing: res.action_routing,
        fraud_probability: res.fraud_probability,
        server_latency_ms: res.system_latency_ms,
        round_trip_ms: Math.round(rtt * 100) / 100,
        brief: res.plain_language_brief,
        reviewer_decision: "Pending",
      };
      setHistory((h) => [...h, record]);
    } catch (e) {
      setError(`Backend disconnected: ${e instanceof Error ? e.message : e}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDecision = (choice: ReviewerDecision, note: string) => {
    setHistory((h) => {
      if (h.length === 0) return h;
      const updated = [...h];
      const last = { ...updated[updated.length - 1] };
      last.reviewer_decision = choice;
      last.decided_at = new Date().toLocaleTimeString("en-GB");
      last.reviewer_note = note;
      updated[updated.length - 1] = last;
      return updated;
    });
  };

  return (
    <div className="app">
      <Sidebar
        useMock={useMock}
        onUseMockChange={setUseMock}
        apiUrl={apiUrl}
        onApiUrlChange={setApiUrl}
      />
      <main className="main">
        <Header useMock={useMock} />
        <MetricsRow history={history} />
        <hr className="divider" />
        <div className="columns">
          <div>
            <TransactionForm onSubmit={handleSubmit} submitting={submitting} />
            {error && <div className="banner error">{error}</div>}
          </div>
          <DecisionPanel history={history} onDecision={handleDecision} />
        </div>
        <hr className="divider" />
        <Tabs
          tabs={[
            { label: "📋 Case log", content: <CaseLogTable history={history} /> },
            { label: "📈 Latency", content: <LatencyChart history={history} /> },
            { label: "🧠 About the model", content: <AboutTab /> },
          ]}
        />
      </main>
    </div>
  );
}
