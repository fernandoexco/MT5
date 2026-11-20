# Análise de Robustez – Estratégia C

> **Aviso metodológico central.** Isto **não** é um relatório gerado pelo Strategy Tester do MT5. O servidor da Clear não oferece símbolos fracionários (sufixo F); os EAs recusam rodar nos lotes disponíveis (100 ações). Os números abaixo vêm do simulador Python (`tools/sim_swing_portfolio.py`) que porta a lógica exata dos EAs sobre candles D1 reais coletados do MT5, com ações inteiras e caixa compartilhado. Não autoriza negociação real.

## 1. Testes de Estresse de Custos e Slippage

Avaliação do impacto de custos operacionais (emolumentos/corretagem) e slippages de execução na carteira compartilhada:

| Cenário de Estresse | Retorno Total | Retorno OOS | Drawdown Máx | Nº Ops |
|---|---|---|---|---|
| Base (0,05%/lado + R$0,05; slip 1 tick entrada, 2 ticks stop) | 2.26% | 0.54% | -1.46% | 32 |
| custos x2 | 1.18% | 0.46% | -1.59% | 28 |
| custos x4 | 0.16% | 0.12% | -1.66% | 26 |
| slippage x3 | 1.18% | 0.43% | -1.56% | 30 |
| custos x2 + slippage x3 | 0.53% | 0.15% | -1.7% | 28 |

> [!NOTE]
> A Estratégia C demonstrou alta resiliência aos custos. Mesmo sob o estresse severo de custos 2× associado a slippage 3×, a estratégia permaneceu em terreno positivo (+0,53% no total e +0,15% OOS). Isso se deve ao reduzido número de trades (32) e ao alto payoff médio (R$ 3,715 por acerto).

## 2. Teste Leave-One-Out por Ativo (Carteira com 9 Ativos)

Mede o impacto da exclusão sistemática de cada um dos ativos do universo elegível:

| Ativo Excluído | Retorno Total | Drawdown Máx | Nº Ops |
|---|---|---|---|
| Sem ITUB4 | 2.53% | -1.39% | 27 |
| Sem BBAS3 | 1.18% | -1.36% | 24 |
| Sem WEGE3 | 1.17% | -2.08% | 28 |
| Sem GGBR4 | 3.21% | -1.45% | 27 |
| Sem PETR4 | 1.15% | -1.43% | 30 |
| Sem VALE3 | 2.26% | -1.46% | 32 |
| Sem BBDC4 | 1.98% | -1.44% | 28 |
| Sem ABEV3 | 2.38% | -1.46% | 31 |
| Sem EGIE3 | 1.72% | -1.79% | 29 |
| Sem SUZB3 | 1.4% | -1.43% | 31 |

O teste leave-one-out confirma que a estratégia não depende exclusivamente de um único papel para fechar positiva. Todos os 10 cenários sem um ativo mantiveram retorno positivo (variando de +1,15% a +3,21%). A exclusão de GGBR4 elevou o retorno para +3,21% (ativo com perdas no período).

## 3. Desempenho Isolado por Ativo (Standalone R$ 500, Max Posições = 1)

Simulação com o capital total alocado exclusivamente a cada ação individualmente:

| Ativo | Retorno Total | Retorno OOS | Nº Ops | Profit Factor | Drawdown Máx |
|---|---|---|---|---|---|
| ITUB4 | -0.21% | -0.06% | 5 | 0.75 | -1.29% |
| BBAS3 | 0.22% | -0.07% | 7 | 1.18 | -1.56% |
| WEGE3 | 0.78% | 0.0% | 4 | 2.67 | -0.79% |
| GGBR4 | -0.95% | -0.36% | 5 | 0.0 | -0.95% |
| PETR4 | 0.86% | 0.0% | 2 | n/d | -0.3% |
| VALE3 | 0.0% | 0.0% | 0 | n/d | 0.0% |
| BBDC4 | 0.28% | 0.32% | 4 | 1.89 | -0.64% |
| ABEV3 | -0.12% | 0.0% | 1 | 0.0 | -0.29% |
| EGIE3 | 0.54% | 0.77% | 3 | 2.27 | -0.53% |
| SUZB3 | 0.62% | 0.0% | 1 | n/d | -0.51% |

## 4. Análise de Concentração de Lucros

- **Número total de operações:** 32
- **Lucro líquido acumulado:** R$ 11.29
- **Maior operação individual (Top 1):** R$ 7.12 (63.1% do lucro total)
- **3 Maiores operações (Top 3):** R$ 17.60 (155.9% do lucro total)
- **Resultado líquido sem as 3 maiores operações:** R$ -6.31

> [!WARNING]
> **Alta vulnerabilidade a outliers:** O resultado total é inteiramente sustentado por 3 operações excelentes. Sem elas, o backtest encerra com prejuízo de R$ -6,31.

## 5. Bootstrap da Expectativa por Operação (5.000 Amostragens)

- **Média amostral:** R$ 0.353 por operação
- **Intervalo de Confiança 95%:** [-0.420; 1.215] R$/op
- **Significância estatística:** Como o intervalo de 95% cruza o zero (inclui valores negativos), **a hipótese nula de expectativa zero ou negativa não pode ser rejeitada** com 95% de confiança.

## 6. Análise de Sensibilidade de Parâmetros

Variação univariada de parâmetros (apenas reporte de robustez, sem seleção post-hoc):

| Parâmetro Testado | Retorno Total | Retorno OOS | Drawdown Máx | Ops | Profit Factor |
|---|---|---|---|---|---|
| {'atr_mult': 1.5} | 0.58% | -0.83% | -2.75% | 42 | 1.09 |
| {'atr_mult': 3.0} | 1.99% | 0.01% | -1.66% | 22 | 1.79 |
| {'reg': 90} | -2.27% | -1.17% | -4.05% | 43 | 0.71 |
| {'reg': 150} | -0.14% | -0.38% | -2.11% | 26 | 0.96 |
| {'fast': 40} | 2.42% | 1.12% | -1.53% | 33 | 1.58 |
| {'slow': 150} | 3.92% | 0.5% | -1.6% | 36 | 1.86 |
| {'prev': 4.0} | 2.26% | 0.54% | -1.46% | 32 | 1.51 |
| {'susp': 8.0} | 2.26% | 0.54% | -1.46% | 32 | 1.51 |

Observa-se que a redução do período de regressão para 90 pregões desestabilizou o canal (-2,27% total), enquanto variações no ATR e médias móveis mantiveram a estratégia em faixas controladas.

## 7. Desempenho por Ano (Consistência Temporal)

| Ano | Retorno da Carteira C |
|---|---|
| 2021 | 0.0% |
| 2022 | -0.12% |
| 2023 | 1.99% |
| 2024 | -0.16% |
| 2025 | 0.89% |
| 2026 | -0.35% |

A estratégia apresentou 2 anos positivos (2023: +1,99%, 2025: +0,89%) e 3 anos com leves oscilações negativas (2022: -0,12%, 2024: -0,16%, 2026: -0,35%). Em 2021 não houve sinais devido ao aquecimento dos indicadores.
