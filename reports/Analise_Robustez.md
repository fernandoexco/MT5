# Análise de Robustez

> **Aviso metodológico central.** Isto **não** é um relatório do Strategy Tester do MT5. O servidor da Clear não oferece símbolos fracionários (sufixo F); os EAs recusam rodar nos lotes disponíveis (ver `Carteira_Consolidada.md`). Os números abaixo vêm de um simulador Python (`tools/sim_swing_portfolio.py`) que porta a lógica dos EAs sobre candles D1 reais lidos do MT5, com ações inteiras. Não autoriza negociação real.

Parâmetros dos EAs mantidos como estavam. As variações abaixo **só reportam sensibilidade**; nada foi escolhido a partir delas nem otimizado.

## Estratégia A

### Custos e slippage (carteira)

| Cenário | Retorno total | Fora da amostra | DD máx | Ops |
|---|---|---|---|---|
| Base (0,05%/lado + R$0,05; slip 1 tick entrada, 2 ticks stop) | 2.65% | 1.96% | -3.68% | 87 |
| custos x2 | -3.13% | 1.22% | -6.54% | 83 |
| custos x4 | -6.29% | -1.78% | -6.74% | 60 |
| slippage x3 | 0.12% | 1.28% | -3.96% | 85 |
| custos x2 + slippage x3 | -3.76% | 0.55% | -6.58% | 82 |

### Sensibilidade de parâmetros

| Parâmetro | Retorno total | Fora da amostra | DD | Ops | PF |
|---|---|---|---|---|---|
| {'atr_mult': 1.5} | 0.51% | 0.13% | -5.48% | 129 | 1.02 |
| {'atr_mult': 3.0} | -0.14% | 0.77% | -3.59% | 54 | 0.98 |
| {'reg': 90} | -0.67% | 2.13% | -5.45% | 112 | 0.97 |
| {'reg': 150} | 1.07% | 1.6% | -3.69% | 72 | 1.1 |
| {'zone': 20.0} | -0.87% | 1.59% | -4.63% | 69 | 0.93 |
| {'zone': 40.0} | 1.81% | 0.0% | -6.39% | 107 | 1.11 |
| {'fast': 40} | 5.18% | 2.44% | -2.98% | 79 | 1.46 |
| {'slow': 150} | 4.82% | 1.59% | -3.39% | 95 | 1.35 |

### Dependência por ativo (standalone R$ 500, 1 posição) e leave-one-out (carteira)

| Ativo | Standalone total | Standalone OOS | Ops | PF | Carteira sem o ativo |
|---|---|---|---|---|---|
| ITUB4 | -0.08% | 0.85% | 13 | 0.95 | 2.73% |
| BBAS3 | -1.52% | -0.01% | 11 | 0.2 | 3.47% |
| WEGE3 | 1.06% | 0.86% | 9 | 1.69 | 1.5% |
| GGBR4 | 1.85% | 1.2% | 8 | 4.29 | 1.49% |
| PETR4 | 2.16% | -0.27% | 13 | 2.81 | 0.81% |
| VALE3 | 0.0% | 0.0% | 0 | n/d | 2.65% |
| BBDC4 | -0.25% | 0.99% | 11 | 0.88 | 2.91% |
| ABEV3 | -2.84% | -1.93% | 14 | 0.19 | 6.17% |
| EGIE3 | -0.09% | 0.28% | 6 | 0.89 | 2.62% |
| SUZB3 | 2.37% | 0.0% | 6 | 3.65 | -0.29% |

Concentração: {'n': 87, 'net': 13.67, 'top1': 9.6236, 'top3': 23.03, 'net_without_top3': -9.37}

Regimes: {'meses_ibov_queda': 24, 'ret_medio_nesses_%': -0.27, 'meses_ibov_alta': 36, 'ret_medio_nesses_alta_%': 0.25}

Bootstrap 95% da expectativa/op (R$): [-0.305, 0.669]

## Estratégia B

### Custos e slippage (carteira)

| Cenário | Retorno total | Fora da amostra | DD máx | Ops |
|---|---|---|---|---|
| Base (0,05%/lado + R$0,05; slip 1 tick entrada, 2 ticks stop) | 3.06% | 0.21% | -3.9% | 124 |
| custos x2 | 0.42% | -0.2% | -5.22% | 120 |
| custos x4 | -6.13% | -2.82% | -7.92% | 96 |
| slippage x3 | 0.47% | -0.49% | -5.18% | 122 |
| custos x2 + slippage x3 | -0.95% | -0.36% | -5.88% | 118 |

### Sensibilidade de parâmetros

| Parâmetro | Retorno total | Fora da amostra | DD | Ops | PF |
|---|---|---|---|---|---|
| {'atr_mult': 1.5} | 4.06% | 0.41% | -5.96% | 170 | 1.06 |
| {'atr_mult': 3.0} | -0.21% | -0.63% | -2.77% | 89 | 0.98 |
| {'brk': 15} | 5.05% | 1.42% | -3.62% | 128 | 1.25 |
| {'brk': 30} | 4.1% | 0.45% | -3.43% | 110 | 1.24 |
| {'exitlow': 7} | 2.51% | 0.0% | -3.64% | 127 | 1.12 |
| {'exitlow': 15} | 3.81% | 1.32% | -4.2% | 120 | 1.19 |
| {'rs': 40} | 7.11% | 0.11% | -4.34% | 127 | 1.36 |
| {'rs': 90} | 5.93% | 0.32% | -3.79% | 107 | 1.36 |

### Dependência por ativo (standalone R$ 500, 1 posição) e leave-one-out (carteira)

| Ativo | Standalone total | Standalone OOS | Ops | PF | Carteira sem o ativo |
|---|---|---|---|---|---|
| ITUB4 | -1.03% | -0.74% | 21 | 0.74 | 2.68% |
| BBAS3 | -1.47% | -2.5% | 21 | 0.74 | 0.83% |
| WEGE3 | 2.92% | 0.97% | 11 | 4.61 | 0.26% |
| GGBR4 | -2.36% | -0.43% | 19 | 0.41 | 5.18% |
| PETR4 | 4.0% | 0.48% | 15 | 3.57 | -1.4% |
| VALE3 | 0.92% | 1.38% | 5 | 1.86 | 2.21% |
| BBDC4 | 0.04% | -0.5% | 14 | 1.02 | 3.05% |
| ABEV3 | -2.06% | 0.17% | 14 | 0.39 | 4.6% |
| EGIE3 | -0.19% | -0.53% | 14 | 0.89 | 2.75% |
| SUZB3 | -0.65% | -0.72% | 4 | 0.22 | 3.4% |

Concentração: {'n': 124, 'net': 15.32, 'top1': 9.9854, 'top3': 23.75, 'net_without_top3': -8.43}

Regimes: {'meses_ibov_queda': 24, 'ret_medio_nesses_%': -0.43, 'meses_ibov_alta': 36, 'ret_medio_nesses_alta_%': 0.38}

Bootstrap 95% da expectativa/op (R$): [-0.27, 0.558]

## Walk-forward

Não executado como otimização: as estratégias têm parâmetros fixos e **nenhum foi otimizado**, então não há etapa de ajuste a validar. Os resultados por ano e por janela (desenvolvimento/validação/fora da amostra) fazem o papel de avaliação sequencial; as janelas são curtas e 2021 não tem operações. Não há significância estatística demonstrável.

## Limitações

- O histórico MT5 começa em 16–17/11/2021; a estratégia A precisa de 200 pregões de aquecimento (primeiros sinais só em ~set/2022), logo a janela de desenvolvimento é efetivamente curta.
- Candles D1 do MT5 sem ajuste comprovado a proventos/eventos; gaps de −26% a −33% em 26/10/2026 (BBAS3, BBDC4, BOVA11), −28,6% em 27/11/2025 (EGIE3) e +16% em 27/06/2024 (SUZB3) sugerem eventos corporativos. Nenhuma operação simulada nesses ativos atravessou esses gaps, mas outras distorções não são descartáveis.
- Universo fixo de 10 ações líquidas de hoje: viés de sobrevivência; sem ativos deslistados.
- Custos (0,05%/lado + R$ 0,05) são premissa dos EAs, não tarifa documentada da Clear; o fracionário real tem spread/liquidez piores.
- Execução diária com abertura do dia seguinte e stop intradiário pela mínima; sem ticks. Gap de stop é preenchido na abertura.
- Risco agregado: cada posição ≤ R$ 2,50 (0,5%), soma das posições abertas ≤ R$ 7,50 (1,5%); ordem de entrada fixa pela lista de ativos (sem ranking).
