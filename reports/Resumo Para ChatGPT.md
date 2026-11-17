# Resumo para ChatGPT — EAs swing B3

## Status

Foram criados dois Expert Advisors independentes em MQL5. Ambos recusam inicialização fora do Strategy Tester e conferem capital inicial de R$ 500, moeda BRL e volume mínimo compatível com lote de até uma ação/cota. Isso bloqueia envio acidental de ordens ao ambiente real; não é autorização nem recomendação de investimento. Os dois compilaram no MetaEditor em 17/11/2026, com **0 erros e 0 avisos** cada.

- Estratégia A: `MQL5/Experts/B3Swing/B3Swing_A_UptrendPullback.mq5`
- Estratégia B: `MQL5/Experts/B3Swing/B3Swing_B_20DayBreakout.mq5`
- Rotinas comuns: `MQL5/Experts/B3Swing/B3SwingCommon.mqh`

**Backtest MT5 de 2021–2026 não executado.** Portanto, os resultados abaixo não estão disponíveis:

| Métrica solicitada | Estratégia A | Estratégia B |
|---|---:|---:|
| Retorno líquido | Não medido | Não medido |
| Drawdown máximo | Não medido | Não medido |
| Fator de lucro | Não medido | Não medido |
| Número de operações | Não medido | Não medido |
| Comparação com Ibovespa | Não medida | Não medida |

Não reutilizei o resultado do backtest anterior (2024–2025), pois ele avalia outra estratégia, com regras e universo diferentes.

## O que falta para produzir os números pedidos

1. Os arquivos históricos locais do projeto incluem COTAHIST de 2023, 2024 e 2025; a série local do Ibovespa cobre 2023-12 a 2025-12. Não há arquivos locais de 2021–2022 nem série de referência até 2026 para validar a janela inteira.
2. A janela 2026 ainda não terminou (data desta execução: 17/11/2026). Um teste até a data disponível teria de ser rotulado como parcial, não como ano de 2026 completo.
3. Não foi fixado um universo histórico de símbolos fracionários da B3 nem foram comprovados os metadados de lote desses símbolos no servidor Clear. Não dá para inferir essa elegibilidade apenas do nome/ticker.
4. Há instalação do terminal e do MetaEditor, mas não foi comprovada neste trabalho a disponibilidade de histórico MT5 completo e utilizável para os símbolos elegíveis e para `IBOV`, nem a configuração de comissão/slippage no Strategy Tester.
5. Os EAs foram compilados, mas não executados no Strategy Tester. Portanto, não há relatório de performance nem validação fora da amostra.

Para a execução, o testador precisará de histórico diário sincronizado dos símbolos negociáveis no mercado fracionário e do benchmark, saldo inicial de R$ 500, custos por ponta e slippage documentados, além da seleção prévia do período e dos conjuntos in-sample/out-of-sample. O símbolo do Ibovespa pode variar por servidor; ajuste `InpBenchmarkSymbol` ao nome efetivamente cadastrado. A série B3 usada deve preservar ações deslistadas e eventos corporativos conhecidos, evitando seleção retrospectiva de ativos.

## Regras e parâmetros codificados

Os parâmetros comuns nos dois EAs são capital inicial R$ 500, risco por operação até R$ 2,50, aplicação máxima de 90% do capital/equity, uma posição por conta do Tester, trava de novas entradas ao atingir perda de 6% do capital inicial e suspensão/fechamento da posição do EA ao atingir 10%. Se a quantidade mínima elevar o risco acima do teto, a operação é descartada. O risco é estimado usando `OrderCalcProfit`, taxas configuráveis por ponta e reserva de slippage do stop; o resultado efetivo do Tester depende também das comissões e do modelo de execução configurados no próprio MT5.

- **A:** regressão linear dos log-fechamentos em 120 pregões; canal inferior; inclinação positiva; SMA50 ascendente e acima da SMA200; toque na zona inferior e fechamento de recuperação acima da máxima anterior. Stop inicial e móvel usam ATR14 × 2,0; fecha também se a inclinação deixa de ser positiva ou as médias/fechamento perdem a tendência.
- **B:** fechamento acima da máxima dos 20 pregões anteriores, volume acima da média dos 20 anteriores e retorno relativo de 60 pregões superior ao Ibovespa. Stop inicial por ATR14 × 2,0; a saída usa a mínima dos 10 pregões anteriores e stop ATR móvel.

O volume usado é o volume real do candle quando fornecido pelo broker; caso contrário, usa tick volume, o que deverá ser anotado no relatório do teste. O EA B exige histórico alinhado do benchmark; ausência de candles do mesmo pregão impede o sinal.

## Limitações metodológicas a registrar no teste futuro

- Comparar as estratégias na mesma lista de símbolos, datas, capital, custos, execução e regras de arredondamento.
- Fixar antes do cálculo o universo elegível, as datas de treino/validação e o corte out-of-sample. Não escolher parâmetros após observar o período de validação.
- Especificar o modelo do Strategy Tester (ticks reais ou aproximação), comissões, spread, slippage, dividendos/splits, survivorship e critérios de liquidez.
- A trava de 6% impede novas entradas; a suspensão de 10% fecha apenas a posição gerida por aquela instância. Cada backtest é de um símbolo/instância e não representa, por si só, uma carteira multissímbolo agregada.
- A regra de frações depende dos metadados do símbolo no servidor. Os EAs não comprovam que a corretora oferece execução fracionária ou que os metadados históricos correspondem aos atuais.
- Os resultados de Tester não demonstram execução, liquidez, proteção overnight nem desempenho futuro.
