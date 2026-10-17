import type { HistoryRecord } from "../types";

interface CaseLogTableProps {
  history: HistoryRecord[];
}

const COLUMNS: (keyof HistoryRecord)[] = [
  "time",
  "type",
  "amount",
  "old_balance",
  "routing",
  "fraud_probability",
  "server_latency_ms",
  "round_trip_ms",
  "brief",
  "reviewer_decision",
  "decided_at",
  "reviewer_note",
];

export default function CaseLogTable({ history }: CaseLogTableProps) {
  if (history.length === 0) {
    return <div className="banner info">No checks run yet.</div>;
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table className="data-table">
        <thead>
          <tr>
            {COLUMNS.map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {history.map((row, i) => (
            <tr key={i}>
              {COLUMNS.map((col) => (
                <td key={col}>{row[col] ?? ""}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
