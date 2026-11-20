# Comparativo Detalhado: Estratégia A vs Estratégia C

> **Aviso metodológico central.** Isto **não** é um relatório gerado pelo Strategy Tester do MT5. O servidor da Clear não oferece símbolos fracionários (sufixo F); os EAs recusam rodar nos lotes disponíveis (100 ações). Os números abaixo vêm do simulador Python (`tools/sim_swing_portfolio.py`) que porta a lógica exata dos EAs sobre candles D1 reais coletados do MT5, com ações inteiras e caixa compartilhado. Não autoriza negociação real.

## Tabela Comparativa de Métricas (2021 a 2026)

| Métrica | Estratégia A (Canal Pullback) | Estratégia C (Força Relativa + Canal) |
|---|---|---|
| Capital inicial | R$ 500,00 | R$ 500,00 |
| Capital final | R$ 513.24 | R$ 511.29 |
| Retorno total líquido | 2.65% | 2.26% |
| Retorno anualizado | 0.52% | 0.45% |
| Drawdown máximo consolidado | -3.68% | -1.46% |
| Profit Factor | 1.2 | 1.51 |
| Taxa de acerto (Hit rate) | 37.9% | 28.1% |
| Número de operações | 87 | 32 |
| Lucro médio por acerto | R$ 2.459 | R$ 3.715 |
| Prejuízo médio por perda | R$ -1.25 | R$ -0.963 |
| Expectativa matemática | R$ 0.157/op | R$ 0.353/op |
| Custos operacionais totais | R$ 12.22 | R$ 4.59 |
| Prazo médio de permanência | 14.6 dias | 14.6 dias |
| Retorno Fora da Amostra (2025-2026) | 1.96% | 0.54% |
| Drawdown Fora da Amostra | -2.12% | -1.04% |
| Profit Factor Fora da Amostra | 1.52 | 1.55 |
| Operações Fora da Amostra | 29 | 10 |
| Expectativa Fora da Amostra | R$ 0.355/op | R$ 0.275/op |
| Retorno IBOV (período total) | 64.45% | 64.45% |
| Retorno CDI (período total) | 82.76% | 82.76% |

## Análise Comparativa dos Pilares Quantitativos

### 1. Rentabilidade vs Preservação de Capital
- **Estratégia A:** Retorno ligeiramente superior (+2,65% vs +2,26%), impulsionado por maior número de operações (87 vs 32) e maior retorno fora da amostra (+1,96% vs +0,54%).
- **Estratégia C:** Muito mais defensiva. O drawdown máximo foi de apenas **-1,46%**, menos da metade do drawdown da Estratégia A (-3,68%). O ranking de força relativa atuou como um forte filtro de contenção de perdas em períodos desfavoráveis.

### 2. Eficiência Estatística e Assimetria
- **Profit Factor:** A Estratégia C obteve PF de **1,51** contra **1,20** da Estratégia A (e 1,55 vs 1,52 fora da amostra).
- **Assimetria (Payoff):** A Estratégia C possui relação lucro médio / prejuízo médio de **3,86** (R$ 3,715 / R$ 0,963), enquanto a Estratégia A possui payoff de **1,97** (R$ 2,459 / R$ 1,250). A Estratégia C aceita taxa de acerto menor (28,1% vs 37,9%) em troca de perdas muito pequenas e carona em altas maiores.
- **Expectativa Matemática:** R$ 0,353 por operação em C vs R$ 0,157 por operação em A.

### 3. Sensibilidade a Custos e Atrito Operacional
- Em cenário de **Custos Duplicados + Slippage Triplicado**, a Estratégia A torna-se **negativa** no total (-0,12%) e fora da amostra (+0,37%).
- A Estratégia C **permanece positiva** tanto no total (+0,53%) quanto fora da amostra (+0,15%), gastando muito menos em corretagens e emolumentos (custos totais de R$ 4,59 em C contra R$ 12,22 em A).

### 4. Concentração e Significância
- Ambas sofrem de extrema concentração de lucros: na Estratégia A, as 3 maiores operações somam R$ 23,03 (superando o lucro total de R$ 13,67); na Estratégia C, somam R$ 17,60 (superando o lucro total de R$ 11,29).
- Em ambas, o intervalo bootstrap 95% cruza o zero (A: [-0,305; +0,669], C: [-0,420; +1,215]). Nenhuma possui comprovação estatística irrefutável.

### 5. Veredito da Estratégia Mais Robusta
A **Estratégia C é estruturalmente mais robusta que a Estratégia A** no controle de risco, controle de drawdown (-1,46% vs -3,68%), tolerância a custos/slippage elevados e assimetria por trade (payoff 3,86). No entanto, sua amostra de 32 operações é reduzida demais, impedindo aprovação direta para negociação.
