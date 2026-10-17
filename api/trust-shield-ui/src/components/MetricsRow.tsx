import type { HistoryRecord } from "../types";
import Metric from "./Metric";

interface MetricsRowProps {
  history: HistoryRecord[];
}

export default function MetricsRow({ history }: MetricsRowProps) {
  const checksRun = history.length;
  const intercepted = history.filter(
    (h) => h.routing === "HARD_INTERCEPT_ESCROW"
  ).length;
  const settled = history.filter(
    (h) => h.routing === "SETTLE_IMMEDIATELY"
  ).length;
  const avgRoundTrip =
    history.length > 0
      ? `${(
          history.reduce((sum, h) => sum + h.round_trip_ms, 0) / history.length
        ).toFixed(1)} ms`
      : "n/a";

  return (
    <div className="metrics-row">
      <Metric label="Checks run" value={checksRun} />
      <Metric label="Intercepted" value={intercepted} />
      <Metric label="Settled" value={settled} />
      <Metric label="Avg round trip" value={avgRoundTrip} />
    </div>
  );
}
