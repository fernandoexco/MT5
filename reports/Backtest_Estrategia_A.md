# Backtest – Estratégia A (reversão em canal de alta)

> **Aviso metodológico central.** Isto **não** é um relatório do Strategy Tester do MT5. O servidor da Clear não oferece símbolos fracionários (sufixo F); os EAs recusam rodar nos lotes disponíveis (ver `Carteira_Consolidada.md`). Os números abaixo vêm de um simulador Python (`tools/sim_swing_portfolio.py`) que porta a lógica dos EAs sobre candles D1 reais lidos do MT5, com ações inteiras. Não autoriza negociação real.

## Lógica
Regressão linear de ln(close) em 120 pregões; inclinação > 0; fechamento > SMA200; SMA50 > SMA50 de 20 pregões atrás e > SMA200; toque na zona inferior (30% inferiores do canal ±2σ) em D-1 ou D-2; fechamento acima da máxima anterior e do limite inferior. Stop inicial 2×ATR(14); stop móvel = máxima desde a entrada − 2×ATR; saída por perda de tendência (inclinação ≤ 0, fechamento < SMA200 ou SMA50 < SMA200).

## Classificação

**REVISÃO NECESSÁRIA**

Retorno líquido positivo mas irrisório (+2,65% em ~5 anos contra CDI +82,8%); fora da amostra +1,96%, PF 1,52, mas a amostra é pequena (29 ops), o IC95% da expectativa inclui zero, as 3 maiores operações superam todo o lucro e custos 2× tornam o total negativo. Não é reprovada (sem prejuízo persistente, risco controlado), mas não há evidência para paper trading.

## Métricas (carteira consolidada, R$ 500, até 3 posições)

| Janela | Ops | Retorno | Anualiz. | DD máx | PF | Acerto | Lucro méd (R$) | Prej. méd (R$) | Expectativa (R$/op) | Dias méd. | Custos (R$) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Período total (2021-11-17 a 2026-11-16) | 87 | 2.65% | 0.52% | -3.68% | 1.2 | 37.9% | 2.459 | -1.25 | 0.157 | 14.6 | 12.22 |
| Desenvolvimento 2021-11 a 2023 | 27 | 0.42% | 0.2% | -3.53% | 0.78 | 33.3% | 1.724 | -1.104 | -0.161 | 13.6 | 3.59 |
| Validação 2024 | 31 | 0.26% | 0.26% | -2.36% | 1.28 | 35.5% | 3.237 | -1.394 | 0.249 | 14.5 | 4.64 |
| Fora da amostra 2025 a 16/11/2026 | 29 | 1.96% | 1.04% | -2.12% | 1.52 | 44.8% | 2.309 | -1.233 | 0.355 | 15.6 | 4.0 |

Capital final: R$ 513.24 (variação de equity R$ 13.24); lucro líquido das operações fechadas R$ 13.67; custos totais R$ 12.22.

Retorno por ano (equity): 2021: 0.0%, 2022: -0.45%, 2023: 0.87%, 2024: 0.26%, 2025: -0.46%, 2026: 2.44% (2021 sem operações: dados começam em 17/11/2021).

## Comparação com benchmarks (retorno do período, sem custos/impostos)

| Janela | Estratégia | IBOV (preço) | BOVA11 | CDI |
|---|---|---|---|---|
| Desenvolvimento | 0.42% | 28.52% | 28.46% | 28.44% |
| 2024 | 0.26% | -10.36% | -10.06% | 10.88% |
| Fora da amostra | 1.96% | 40.75% | 42.05% | 28.34% |
| Total | 2.65% | 64.45% | 67.84% | 82.76% |

Nenhuma das duas bateu o CDI em janela alguma; frente ao IBOV só superaram em 2024, ano de queda do índice.

## Estatística

Intervalo bootstrap 95% da expectativa por operação (R$): [-0.305, 0.669] — inclui zero; **sem evidência estatística de vantagem**. Amostra: 87 operações, autocorrelacionadas entre ativos; o bootstrap simples ignora isso.

Concentração: lucro líquido R$ 13.67; as 3 maiores operações somam R$ 23.03; sem elas o resultado é R$ -9.37.

Regime: meses de queda do IBOV (24): retorno médio mensal -0.27%; meses de alta (36): 0.25%.

Posições abertas ao fim: {'GGBR4': {'qty': 1, 'entry': 24.96, 'last': 24.6}}. Suspensão de 10% acionada: não. O drawdown máximo ficou abaixo do limite preventivo de 6%.
