# Backtest – Estratégia B (rompimento de 20 pregões)

> **Aviso metodológico central.** Isto **não** é um relatório do Strategy Tester do MT5. O servidor da Clear não oferece símbolos fracionários (sufixo F); os EAs recusam rodar nos lotes disponíveis (ver `Carteira_Consolidada.md`). Os números abaixo vêm de um simulador Python (`tools/sim_swing_portfolio.py`) que porta a lógica dos EAs sobre candles D1 reais lidos do MT5, com ações inteiras. Não autoriza negociação real.

## Lógica
Fechamento de D-1 acima da máxima dos 20 pregões anteriores, volume de D-1 acima da média de 20, retorno de 60 pregões maior que o do IBOV. Stop inicial 2×ATR(14); stop móvel = máx(mínima de 10 pregões, preço − 2×ATR) quando em lucro; saída se fechamento < mínima dos 10 pregões anteriores.

## Classificação

**REVISÃO NECESSÁRIA (próxima de reprovada)**

Retorno +3,06% no total, mas só +0,21% fora da amostra (PF 1,03, DD −3,67%); negativa em 2024 e 2026; com custos 2× + slippage 3× o fora da amostra é negativo; com apenas 1 posição o total é −0,56%. Sem evidência estatística.

## Métricas (carteira consolidada, R$ 500, até 3 posições)

| Janela | Ops | Retorno | Anualiz. | DD máx | PF | Acerto | Lucro méd (R$) | Prej. méd (R$) | Expectativa (R$/op) | Dias méd. | Custos (R$) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Período total (2021-11-17 a 2026-11-16) | 124 | 3.06% | 0.61% | -3.9% | 1.15 | 39.5% | 2.371 | -1.345 | 0.124 | 17.3 | 17.32 |
| Desenvolvimento 2021-11 a 2023 | 48 | 3.98% | 1.86% | -2.92% | 1.26 | 39.6% | 2.524 | -1.311 | 0.207 | 17.5 | 6.57 |
| Validação 2024 | 32 | -1.08% | -1.09% | -3.0% | 1.18 | 50.0% | 1.794 | -1.523 | 0.135 | 16.8 | 4.62 |
| Fora da amostra 2025 a 16/11/2026 | 44 | 0.21% | 0.11% | -3.67% | 1.03 | 31.8% | 2.822 | -1.281 | 0.024 | 17.5 | 6.13 |

Capital final: R$ 515.32 (variação de equity R$ 15.32); lucro líquido das operações fechadas R$ 15.32; custos totais R$ 17.32.

Retorno por ano (equity): 2021: 0.0%, 2022: 2.05%, 2023: 1.89%, 2024: -1.08%, 2025: 1.33%, 2026: -1.11% (2021 sem operações: dados começam em 17/11/2021).

## Comparação com benchmarks (retorno do período, sem custos/impostos)

| Janela | Estratégia | IBOV (preço) | BOVA11 | CDI |
|---|---|---|---|---|
| Desenvolvimento | 3.98% | 28.52% | 28.46% | 28.44% |
| 2024 | -1.08% | -10.36% | -10.06% | 10.88% |
| Fora da amostra | 0.21% | 40.75% | 42.05% | 28.34% |
| Total | 3.06% | 64.45% | 67.84% | 82.76% |

Nenhuma das duas bateu o CDI em janela alguma; frente ao IBOV só superaram em 2024, ano de queda do índice.

## Estatística

Intervalo bootstrap 95% da expectativa por operação (R$): [-0.27, 0.558] — inclui zero; **sem evidência estatística de vantagem**. Amostra: 124 operações, autocorrelacionadas entre ativos; o bootstrap simples ignora isso.

Concentração: lucro líquido R$ 15.32; as 3 maiores operações somam R$ 23.75; sem elas o resultado é R$ -8.43.

Regime: meses de queda do IBOV (24): retorno médio mensal -0.43%; meses de alta (36): 0.38%.

Posições abertas ao fim: nenhuma. Suspensão de 10% acionada: não. O drawdown máximo ficou abaixo do limite preventivo de 6%.
