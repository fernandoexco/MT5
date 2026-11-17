# Comparativo das Estratégias A e B

> **Aviso metodológico central.** Isto **não** é um relatório do Strategy Tester do MT5. O servidor da Clear não oferece símbolos fracionários (sufixo F); os EAs recusam rodar nos lotes disponíveis (ver `Carteira_Consolidada.md`). Os números abaixo vêm de um simulador Python (`tools/sim_swing_portfolio.py`) que porta a lógica dos EAs sobre candles D1 reais lidos do MT5, com ações inteiras. Não autoriza negociação real.

| Métrica | A | B |
|---|---|---|
| Retorno total | 2.65% | 3.06% |
| Anualizado | 0.52% | 0.61% |
| DD máx | -3.68% | -3.9% |
| Profit factor | 1.2 | 1.15 |
| Acerto | 37.9% | 39.5% |
| Operações | 87 | 124 |
| Expectativa R$/op | 0.157 | 0.124 |
| Custos R$ | 12.22 | 17.32 |
| OOS retorno | 1.96% | 0.21% |
| OOS DD | -2.12% | -3.67% |
| OOS PF | 1.52 | 1.03 |
| OOS ops | 29 | 44 |
| IBOV / BOVA11 / CDI (total) | 64.45% / 67.84% / 82.76% | idem |

**Melhor ajustada ao risco: A**, por pequena margem (OOS +1,96% vs +0,21%, PF 1,52 vs 1,03, DD OOS −2,1% vs −3,7%), mas sem significância (IC95% da expectativa inclui zero em ambas), dependente de 3 operações e negativa no total com custos 2×. Nenhuma bate CDI/IBOV. Ambas: REVISÃO NECESSÁRIA; nenhuma foi aprovada para paper trading.

Detalhes: `Backtest_Estrategia_A.md`, `Backtest_Estrategia_B.md`, `Analise_Robustez.md`, `Carteira_Consolidada.md`. O estudo Python anterior (2024–2025) permanece em `reports/backtest/`.
