# Comparativo das estrategias swing

## EAs MQL5 A e B

Os EAs `B3Swing_A_UptrendPullback.mq5` e `B3Swing_B_20DayBreakout.mq5`
compilaram, mas **nao foram executados no Strategy Tester**. Nao existem
resultados medidos para retorno liquido, drawdown, fator de lucro, quantidade
de operacoes ou comparacao com o Ibovespa. Nao ha base valida para dizer qual
dos dois foi mais robusto.

| Metrica | A — reversao no canal | B — rompimento de 20 pregoes |
|---|---:|---:|
| Retorno liquido | Nao medido | Nao medido |
| Drawdown maximo | Nao medido | Nao medido |
| Fator de lucro | Nao medido | Nao medido |
| Operacoes | Nao medidas | Nao medidas |
| Ibovespa | Nao comparado | Nao comparado |

## Estudo historico anterior (nao e resultado dos EAs A/B)

Existe um estudo Python separado, de 02/01/2024 a 30/12/2025, para a versao
anterior `swing-v1`. Ele nao e um backtest dos EAs MQL5 publicados e nao deve
ser usado para ranquea-los:

| Metrica do estudo swing-v1 | Resultado |
|---|---:|
| Valor final apos custos | R$ 479,55 |
| Retorno acumulado | -4,09% |
| Drawdown maximo | -4,38% |
| Fator de lucro | 0,30 |
| Operacoes encerradas | 14 |
| Ibovespa no mesmo intervalo | +20,08% |

O [relatorio completo](backtest/RELATORIO.md) documenta as hipoteses e
limitacoes. Dados diarios brutos e caches de cotacoes nao foram publicados.
