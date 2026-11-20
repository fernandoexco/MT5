# Resumo Executivo – Estratégia C (Para ChatGPT / Análise Quantitativa)

> **Aviso metodológico central.** Isto **não** é um relatório gerado pelo Strategy Tester do MT5. O servidor da Clear não oferece símbolos fracionários (sufixo F); os EAs recusam rodar nos lotes disponíveis (100 ações). Os números abaixo vêm do simulador Python (`tools/sim_swing_portfolio.py`) que porta a lógica exata dos EAs sobre candles D1 reais coletados do MT5, com ações inteiras e caixa compartilhado. Não autoriza negociação real.

## 1. Identificação do Projeto
- **Estratégia:** C — Swing Trade com Ranking de Força Relativa, Canal de Regressão Logarítmica e Gestão de Risco.
- **Plataforma:** MQL5 (`MQL5/Experts/B3Swing/B3Swing_C_RelativeStrength.mq5`) e Simulador Consolidado Python (`tools/sim_swing_portfolio.py`).
- **Ativos:** ITUB4, BBAS3, WEGE3, GGBR4, PETR4, VALE3, BBDC4, ABEV3, EGIE3, SUZB3 (10 ações líquidas B3) + IBOV.
- **Período:** 17/11/2021 a 16/11/2026 (1.248 barras D1 por ativo).
- **Divisão:** Desenvolvimento (2021–2023), Validação (2024), Fora da Amostra (2025–16/11/2026).
- **Capital Inicial:** R$ 500,00 | Caixa compartilhado | Posições simultâneas: até 3 | Sem alavancagem.
- **Custos:** 0,05%/lado + R$ 0,05 fixo/lado | Slippage: 1 tick entrada, 2 ticks stop.

## 2. Resumo Numérico Comparativo (A x C)
| Indicador | Estratégia A | Estratégia C | Benchmark (IBOV / CDI) |
|---|---|---|---|
| Capital Final | R$ 513.24 | R$ 511.29 | - |
| Retorno Total Líquido | +2.65% | +2.26% | IBOV: +64,45% / CDI: +82,76% |
| Retorno Anualizado | +0.52% | +0.45% | - |
| Drawdown Máximo | -3.68% | -1.46% | - |
| Profit Factor | 1.2 | 1.51 | - |
| Taxa de Acerto | 37.9% | 28.1% | - |
| Total de Operações | 87 | 32 | - |
| Lucro Médio / Prejuízo Médio | R$ 2.459 / R$ -1.25 | R$ 3.715 / R$ -0.963 | - |
| Relação Payoff (Win/Loss) | 1,97 | 3,86 | - |
| Expectativa Matemática | R$ 0.157/op | R$ 0.353/op | - |
| Retorno Fora da Amostra (OOS) | +1.96% | +0.54% | IBOV: +40,75% / CDI: +28,34% |
| Drawdown Fora da Amostra | -2.12% | -1.04% | - |
| Profit Factor Fora da Amostra | 1.52 | 1.55 | - |
| Operações Fora da Amostra | 29 | 10 | - |
| Custos Totais | R$ 12.22 | R$ 4.59 | - |
| Custos 2× + Slippage 3× | -0,12% (prejuízo) | +0,53% (positivo) | - |
| Bootstrap IC 95% Expectativa | [-0,305; +0,669] | [-0,420; +1,215] | Ambos cruzam zero |
| Concentração (Top 3 trades) | R$ 23,03 (Total: 13,67) | R$ 17,60 (Total: 11,29) | Ambos dependem de outliers |

## 3. Diagnóstico e Classificação
- **Classificação Formal:** **REVISÃO NECESSÁRIA**.
- **Motivação:** A Estratégia C superou a Estratégia A em qualidade de risco, gerando um drawdown máximo minúsculo (-1,46%), melhor profit factor (1,51), excelente assimetria de ganhos (payoff 3,86) e sobrevida operacional a custos duplicados e slippage triplicado (+0,53%).
- **Impedimentos para Aprovação:**
  1. Amostra muito pequena: apenas 32 operações em 5 anos (10 fora da amostra).
  2. Intervalo de confiança bootstrap cruza zero, sem significância estatística conclusiva a 95%.
  3. Extrema dependência de 3 trades (sem o top 3, resultado seria -R$ 6,31).
  4. Retorno líquido irrisório (+2,26%) ante o CDI (+82,76%).
- **NÃO AUTORIZADA PARA PAPER TRADING OU EXECUÇÃO REAL.**

## 4. O que Foi Implementado e Testado
- Implementação MQL5: `MQL5/Experts/B3Swing/B3Swing_C_RelativeStrength.mq5` (compilado no MetaEditor build 6230 com 0 erros e 0 warnings).
- Implementação Python: `tools/sim_swing_portfolio.py` com simulador multiativo, ranking de percentis, canal log-linear e travas de High-Water Mark.
- Testes Unitários Automatizados: `tools/test_strategy_c.py` (14 testes cobrindo ranking, canais, stops, dimensionamento, limites de risco, gaps, ausência de look-ahead e bloqueio de ordens reais — 100% aprovados).
- Análises de Robustez: Custos 2x/4x, slippage 3x, leave-one-out em 10 ativos, sensibilidade paramétrica, bootstrap de 5.000 amostragens, regimes de mercado.
- Não houve execução de ordens reais nem alteração dos parâmetros da Estratégia A.
