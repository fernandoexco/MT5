# Backtest – Estratégia C (Força Relativa e Canal de Alta)

> **Aviso metodológico central.** Isto **não** é um relatório gerado pelo Strategy Tester do MT5. O servidor da Clear não oferece símbolos fracionários (sufixo F); os EAs recusam rodar nos lotes disponíveis (100 ações). Os números abaixo vêm do simulador Python (`tools/sim_swing_portfolio.py`) que porta a lógica exata dos EAs sobre candles D1 reais coletados do MT5, com ações inteiras e caixa compartilhado. Não autoriza negociação real.

## Lógica
Ranking diário de Força Relativa (RS20, RS60, RS120 vs IBOV) com pesos 0,40 / 0,35 / 0,25 sobre percentis transversais. Filtros obrigatórios: RS20 > 0, RS60 > 0, Fechamento > SMA50, SMA50 > SMA200, SMA50 ascendente (10 pregões). TOP 3 elegíveis. Canal de regressão logarítmica de 120 pregões com bandas ±2σ; compra na zona entre a banda inferior e a linha central, com confirmação (fechamento > máxima anterior). Stop inicial 2×ATR(14); stop móvel pelo maior fechamento − 2×ATR; saída adicional se fechamento < SMA50 ou inclinação ≤ 0. Risco máx 0,5% por operação, agregado 1,5%, travas de 6% (preventiva) e 10% (suspensão/liquidação sobre o maior patrimônio).

## Classificação

**REVISÃO NECESSÁRIA**

Apresentou lucro líquido positivo (+2,26% total, +0,54% fora da amostra) com drawdown extremamente reduzido (-1,46%) e profit factor saudável (1,51). Além disso, sobreviveu a custos 2× e slippage 3× (+0,53%). Porém, o número de operações é diminuto (apenas 32 em 5 anos, sendo 10 fora da amostra), o intervalo bootstrap de 95% da expectativa inclui zero [-0,42; +1,22], as 3 maiores operações concentram todo o lucro (sem elas o resultado seria -R$ 6,31), e o ganho acumulado é irrisório frente ao CDI (+82,76%). Não há evidência estatística suficiente para autorizar paper trading.

## Métricas (carteira consolidada, R$ 500, até 3 posições)

| Janela | Ops | Retorno | Anualiz. | DD máx | PF | Acerto | Lucro méd (R$) | Prej. méd (R$) | Expectativa (R$/op) | Dias méd. | Custos (R$) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Período total (2021-11-17 a 2026-11-16) | 32 | 2.26% | 0.45% | -1.46% | 1.51 | 28.1% | 3.715 | -0.963 | 0.353 | 14.6 | 4.59 |
| Desenvolvimento 2021-11 a 2023 | 12 | 1.87% | 0.88% | -1.11% | 2.25 | 41.7% | 3.359 | -1.065 | 0.779 | 20.7 | 1.66 |
| Validação 2024 | 10 | -0.16% | -0.16% | -1.44% | 0.92 | 20.0% | 4.431 | -1.208 | -0.08 | 12.1 | 1.53 |
| Fora da amostra 2025 a 16/11/2026 | 10 | 0.54% | 0.29% | -1.04% | 1.55 | 20.0% | 3.887 | -0.628 | 0.275 | 9.7 | 1.4 |

Capital final: R$ 511.29 (variação de equity R$ 11.29); lucro líquido das operações fechadas R$ 11.29; custos operacionais totais R$ 4.59.

Retorno por ano (equity): 2021: 0.0%, 2022: -0.12%, 2023: 1.99%, 2024: -0.16%, 2025: 0.89%, 2026: -0.35% (2021 sem operações por falta de barras de aquecimento para SMA200).

## Comparação com Benchmarks (retorno acumulado do período)

| Janela | Estratégia C | IBOV (preço) | BOVA11 | CDI |
|---|---|---|---|---|
| Desenvolvimento (2021-11 a 2023) | 1.87% | 28.52% | 28.46% | 28.44% |
| Validação (2024) | -0.16% | -10.36% | -10.06% | 10.88% |
| Fora da amostra (2025 a 16/11/2026) | 0.54% | 40.75% | 42.05% | 28.34% |
| Total | 2.26% | 64.45% | 67.84% | 82.76% |

Em nenhuma janela a estratégia superou o CDI. Frente ao Ibovespa, superou em 2024 (ano em que o IBOV caiu 10,36% e a estratégia oscilou apenas -0,16%).

## Análise Estatística

- **Intervalo Bootstrap 95% da Expectativa por Operação:** [-0.42, 1.215] R$/op. Cruzando o zero, demonstrando ausência de significância estatística robusta (p > 0,05).
- **Amostra:** 32 operações fechadas em ~5 anos (média de 6,4 operações/ano). A baixa rotatividade é consequência direta do filtro restritivo combinado (ranking + canal + confirmação) e da restrição de capital (R$ 500).
- **Concentração de Lucros:** Lucro líquido total R$ 11.29; a maior operação (top 1) gerou R$ 7.12; as 3 maiores somam R$ 17.60. Sem as 3 maiores, o resultado líquido é R$ -6.31.
- **Comportamento por Regime de Mercado:** Em meses de queda do IBOV (24), retorno médio mensal de -0.1%; em meses de alta (36), retorno médio de 0.13%.
- **Controle de Risco e Posições:** Posições abertas ao final: nenhuma. Suspensão de 10% acionada: Não. O drawdown máximo (-1,46%) jamais ameaçou a trava preventiva de 6% nem a trava de 10%.
