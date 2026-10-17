interface MetricProps {
  label: string;
  value: string | number;
}

export default function Metric({ label, value }: MetricProps) {
  return (
    <div className="metric">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  );
}
