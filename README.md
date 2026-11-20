# B3 Swing Expert Advisors (MQL5)

Três Expert Advisors long-only para testes e estudos exploratórios de swing trade na B3:

- **A — Uptrend pullback:** regressão linear em log, filtros de média móvel (SMA50/SMA200),
  recuperação da banda inferior e condução de stop via ATR(14).
- **B — 20-day breakout:** rompimento de preço de 20 pregões com volume acima da média e
  força relativa positiva frente ao Ibovespa, stop ATR e saída pela mínima de 10 pregões.
- **C — Relative strength ranking & trend channel:** ranking diário por percentis transversais
  de força relativa (RS20, RS60, RS120 vs IBOV), canal de alta log-linear ±2σ, zona de entrada
  inferior/central com confirmação, condução por maior fechamento − 2×ATR e travas de High-Water Mark.

Todos os EAs são restritos exclusivamente ao MetaTrader 5 Strategy Tester. Exigem conta de teste
em BRL com saldo inicial de R$ 500,00, operam sem alavancagem ou venda a descoberto e descartam
entradas quando o lote mínimo excede os limites de risco ou capital disponível.

## Arquivos Principais

- `MQL5/Experts/B3Swing/B3Swing_A_UptrendPullback.mq5`
- `MQL5/Experts/B3Swing/B3Swing_B_20DayBreakout.mq5`
- `MQL5/Experts/B3Swing/B3Swing_C_RelativeStrength.mq5`
- `MQL5/Experts/B3Swing/B3SwingCommon.mqh`
- `tools/sim_swing_portfolio.py` — Simulador multiativo consolidado para carteira com caixa compartilhado.
- `tools/test_strategy_c.py` — Testes unitários automatizados da Estratégia C.
- `reports/Backtest_Estrategia_C.md` — Relatório de backtest consolidado da Estratégia C.
- `reports/Comparativo_A_C.md` — Comparativo quantitativo detalhado entre a Estratégia A e a Estratégia C.
- `reports/Robustez_Estrategia_C.md` — Testes de estresse de custos, slippage, sensibilidade e leave-one-out.
- `reports/Resumo_Estrategia_C_ChatGPT.md` — Resumo executivo integral para revisão por LLM/ChatGPT.

## Status de Validação

- Compilação: Os EAs A, B e C compilam no MetaEditor (build 6230) com 0 erros e 0 avisos.
- Classificação: **REVISÃO NECESSÁRIA** (resultados líquidos positivos e controles funcionais, mas amostra pequena, ausência de significância estatística no IC 95% e dependência de poucas operações).
- Não há autorização para negociação real ou paper trading automatizado.
