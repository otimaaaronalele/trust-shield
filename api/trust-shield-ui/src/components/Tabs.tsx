import { useState, type ReactNode } from "react";

interface TabsProps {
  tabs: { label: string; content: ReactNode }[];
}

export default function Tabs({ tabs }: TabsProps) {
  const [active, setActive] = useState(0);

  return (
    <div className="tabs">
      <div className="tab-bar">
        {tabs.map((tab, i) => (
          <button
            key={tab.label}
            className={i === active ? "active" : ""}
            onClick={() => setActive(i)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div>{tabs[active].content}</div>
    </div>
  );
}
