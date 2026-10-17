"""Fairness table from DS1's test_predictions.csv (amount bands as a proxy for income).
Usage: python value_band.py test_predictions.csv
"""
import sys, os
import pandas as pd

df = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "test_predictions.csv")
df["band"] = pd.qcut(df["amount"], 4, duplicates="drop")
lines = ["| Amount band | Transactions | Fraud | Honest sent to REVIEW | Honest HOLD | Honest flagged rate | Fraud caught |",
         "|---|---|---|---|---|---|---|"]
for band, g in df.groupby("band", observed=True):
    honest, fraud = g[g.y_true == 0], g[g.y_true == 1]
    rev = int((honest.decision == "REVIEW").sum())
    hold = int((honest.decision == "HOLD").sum())
    rate = (rev + hold) / len(honest) if len(honest) else float("nan")
    caught = (fraud.decision != "RELEASE").mean() if len(fraud) else float("nan")
    lines.append(f"| {band.left:,.0f} to {band.right:,.0f} | {len(g):,} | {len(fraud):,} | {rev} | {hold} | {rate:.2%} | {caught:.1%} |")
text = "\n".join(lines)
print(text)
os.makedirs("eval", exist_ok=True)
open("eval/value_band.md", "w", encoding="utf-8").write(text)
print("\nsaved to eval/value_band.md")
