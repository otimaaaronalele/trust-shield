import { useState } from "react";
import { testConnection } from "../api";

interface SidebarProps {
  useMock: boolean;
  onUseMockChange: (v: boolean) => void;
  apiUrl: string;
  onApiUrlChange: (v: string) => void;
}

export default function Sidebar({
  useMock,
  onUseMockChange,
  apiUrl,
  onApiUrlChange,
}: SidebarProps) {
  const [status, setStatus] = useState<"idle" | "ok" | "fail">("idle");

  const handleTestConnection = async () => {
    const ok = await testConnection(apiUrl);
    setStatus(ok ? "ok" : "fail");
  };

  return (
    <aside className="sidebar">
      <h2>⚙️ System settings</h2>
      <div className="field-group">
        <label className="field-label">
          <input
            type="checkbox"
            checked={useMock}
            onChange={(e) => onUseMockChange(e.target.checked)}
            style={{ marginRight: 8 }}
          />
          Mock mode (no backend)
        </label>
      </div>
      <div className="field-group">
        <label className="field-label">API URL</label>
        <input
          type="text"
          value={apiUrl}
          onChange={(e) => onApiUrlChange(e.target.value)}
        />
      </div>
      <button className="full" onClick={handleTestConnection}>
        Test connection
      </button>
      {status === "ok" && (
        <div className="banner success" style={{ marginTop: 10 }}>
          Server reachable
        </div>
      )}
      {status === "fail" && (
        <div className="banner error" style={{ marginTop: 10 }}>
          Cannot reach server
        </div>
      )}
      <p className="caption" style={{ marginTop: 14 }}>
        Switch mock mode off once the SWE's server is running.
      </p>
    </aside>
  );
}
