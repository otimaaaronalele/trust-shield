import Metric from "./Metric";

const LAYER_ROWS = [
  {
    layer: "Tier 1: rule (auto-hold)",
    flagged: 1596,
    trueFraud: 1596,
    honestHeld: 0,
    precision: "1.000",
  },
  {
    layer: "Tier 2: model only (human review)",
    flagged: 273,
    trueFraud: 58,
    honestHeld: 215,
    precision: "0.2125",
  },
  {
    layer: "Combined",
    flagged: 1869,
    trueFraud: 1654,
    honestHeld: 215,
    precision: "0.885",
  },
];

export default function AboutTab() {
  return (
    <div>
      <h3 className="subheader">How the system decides</h3>
      <ol>
        <li>
          <strong>Rule:</strong> amount equals the sender's balance (full
          drain) → <strong>HOLD</strong>
        </li>
        <li>
          <strong>Model:</strong> otherwise, a LightGBM score at or above the
          threshold → <strong>REVIEW</strong> by a human
        </li>
        <li>
          <strong>Otherwise</strong> → <strong>RELEASE</strong>
        </li>
      </ol>
      <p>
        The model uses only fields known before approval: type, amount,
        sender balance, recipient balance.
      </p>

      <h3 className="subheader">Test-set results</h3>
      <p className="caption">
        PaySim synthetic data, time-based split, test set scored once. Source:
        DS1 notebook.
      </p>
      <div className="metrics-row">
        <Metric label="Recall" value="1.000" />
        <Metric label="Precision" value="0.885" />
        <Metric label="False-positive rate" value="0.43%" />
        <Metric label="F1" value="0.939" />
      </div>

      <p>
        <strong>
          What each layer contributes (test set, 51,286 transactions, 1,654
          fraud)
        </strong>
      </p>
      <table className="data-table">
        <thead>
          <tr>
            <th>Layer</th>
            <th>Flagged</th>
            <th>True fraud</th>
            <th>Honest customers held</th>
            <th>Precision</th>
          </tr>
        </thead>
        <tbody>
          {LAYER_ROWS.map((row) => (
            <tr key={row.layer}>
              <td>{row.layer}</td>
              <td>{row.flagged}</td>
              <td>{row.trueFraud}</td>
              <td>{row.honestHeld}</td>
              <td>{row.precision}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="banner warning" style={{ marginTop: 16 }}>
        Limitations: PaySim is synthetic and its fraud patterns are simple, so
        these figures do not represent real-world performance. The rule's
        perfect precision reflects how PaySim generates fraud. The test set
        has a 3.2% fraud rate (training: 0.20%), so precision will differ
        elsewhere. Results come from a replay of completed records.
      </div>
    </div>
  );
}
