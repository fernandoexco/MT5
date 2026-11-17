# B3 Swing Expert Advisors (MQL5)

Two long-only Expert Advisors for exploratory B3 swing-trading tests:

- **A — Uptrend pullback:** regression channel, moving-average trend filters,
  lower-band recovery, and ATR-based stop management.
- **B — 20-day breakout:** price breakout with above-average volume and
  positive relative strength versus Ibovespa, with ATR stop and 10-day-low exit.

Both EAs are restricted to the MetaTrader 5 Strategy Tester. They require a
BRL test account with R$500 initial balance, do not use leverage or short
positions, and skip entries when the minimum lot exceeds the configured risk
or capital limits. This restriction does not establish that a broker offers
fractional B3 trading.

## Files

- `MQL5/Experts/B3Swing/B3Swing_A_UptrendPullback.mq5`
- `MQL5/Experts/B3Swing/B3Swing_B_20DayBreakout.mq5`
- `MQL5/Experts/B3Swing/B3SwingCommon.mqh`
- `reports/Resumo Para ChatGPT.md` — implementation status, unavailable
  backtest metrics, and methodological limitations.

## Validation status

The EAs compiled in MetaEditor with zero errors and zero warnings. A 2021–2026
Strategy Tester run and out-of-sample validation have **not** been completed.
No performance figures are reported. Do not treat these source files or the
compilation result as evidence of profitability or as authorization for live
trading.
