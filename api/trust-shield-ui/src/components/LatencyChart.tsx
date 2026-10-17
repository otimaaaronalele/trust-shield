import type { HistoryRecord } from "../types";

interface LatencyChartProps {
  history: HistoryRecord[];
}

export default function LatencyChart({ history }: LatencyChartProps) {
  if (history.length === 0) {
    return <div className="banner info">No checks run yet.</div>;
  }

  const values = history.map((h) => h.round_trip_ms);
  const width = 600;
  const height = 200;
  const padding = 20;
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = max - min || 1;

  const points = values.map((v, i) => {
    const x =
      values.length === 1
        ? padding
        : padding + (i / (values.length - 1)) * (width - padding * 2);
    const y = height - padding - ((v - min) / range) * (height - padding * 2);
    return `${x},${y}`;
  });

  return (
    <div className="chart-wrap">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        height={height}
        preserveAspectRatio="none"
      >
        <polyline
          points={points.join(" ")}
          fill="none"
          stroke="#00c2a8"
          strokeWidth={2}
        />
        {points.map((p, i) => {
          const [x, y] = p.split(",");
          return <circle key={i} cx={x} cy={y} r={3} fill="#00c2a8" />;
        })}
      </svg>
    </div>
  );
}
