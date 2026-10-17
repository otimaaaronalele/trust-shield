interface HeaderProps {
  useMock: boolean;
}

export default function Header({ useMock }: HeaderProps) {
  return (
    <>
      <h1 className="title">🛡️ Trust-Shield: Risk Operations Console</h1>
      <p className="caption">Real-time transaction screening with human review</p>
      {useMock ? (
        <div className="banner warning">
          🧪 DEMO MODE: results are simulated and do not come from the fraud model.
        </div>
      ) : (
        <div className="banner success">
          🟢 LIVE: connected to the Trust-Shield model server.
        </div>
      )}
    </>
  );
}
