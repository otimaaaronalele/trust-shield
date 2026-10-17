import { useState } from "react";
import type { TxType } from "../types";

interface TransactionFormProps {
  onSubmit: (fields: {
    txType: TxType;
    amount: number;
    oldBal: number;
    nameOrig: string;
    nameDest: string;
    oldDest: number;
  }) => void;
  submitting: boolean;
}

export default function TransactionForm({
  onSubmit,
  submitting,
}: TransactionFormProps) {
  const [txType, setTxType] = useState<TxType>("CASH_OUT");
  const [amount, setAmount] = useState(150000.0);
  const [oldBal, setOldBal] = useState(150000.0);
  const [nameOrig, setNameOrig] = useState("C01");
  const [nameDest, setNameDest] = useState("M01");
  const [oldDest, setOldDest] = useState(0.0);

  const presetNormal = () => {
    setAmount(5000.0);
    setOldBal(150000.0);
  };

  const presetDrain = () => {
    setAmount(150000.0);
    setOldBal(150000.0);
  };

  return (
    <div>
      <h3 className="subheader">Transaction</h3>
      <div className="field-group">
        <label className="field-label">Type</label>
        <select
          value={txType}
          onChange={(e) => setTxType(e.target.value as TxType)}
        >
          <option value="CASH_OUT">CASH_OUT</option>
          <option value="TRANSFER">TRANSFER</option>
        </select>
      </div>
      <div className="row-2">
        <button onClick={presetNormal}>Normal cash-out</button>
        <button onClick={presetDrain}>Full wallet drain</button>
      </div>
      <div className="field-group">
        <label className="field-label">Amount</label>
        <input
          type="number"
          min={0}
          value={amount}
          onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
        />
      </div>
      <div className="field-group">
        <label className="field-label">Sender old balance</label>
        <input
          type="number"
          min={0}
          value={oldBal}
          onChange={(e) => setOldBal(parseFloat(e.target.value) || 0)}
        />
      </div>
      {amount > oldBal && (
        <div className="banner warning">
          Amount exceeds the sender's balance, so this transaction is inconsistent.
        </div>
      )}
      <details className="expander">
        <summary>Advanced fields</summary>
        <div className="field-group">
          <label className="field-label">Sender ID</label>
          <input
            type="text"
            value={nameOrig}
            onChange={(e) => setNameOrig(e.target.value)}
          />
        </div>
        <div className="field-group">
          <label className="field-label">Recipient ID</label>
          <input
            type="text"
            value={nameDest}
            onChange={(e) => setNameDest(e.target.value)}
          />
        </div>
        <div className="field-group">
          <label className="field-label">Recipient old balance</label>
          <input
            type="number"
            min={0}
            value={oldDest}
            onChange={(e) => setOldDest(parseFloat(e.target.value) || 0)}
          />
        </div>
      </details>
      <button
        className="primary"
        disabled={submitting}
        onClick={() =>
          onSubmit({ txType, amount, oldBal, nameOrig, nameDest, oldDest })
        }
      >
        🔍 Trigger System Check
      </button>
    </div>
  );
}
