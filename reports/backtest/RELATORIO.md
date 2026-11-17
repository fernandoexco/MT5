# Backtest histórico de swing — 2024 e 2025

**Resultado estimado desfavorável: os R$ 500 terminaram em R$ 479,55 (-4,09%), após custos e incluindo R$ 1,36 em proventos/recebíveis.**
Não houve envio de ordens reais. Este é um modelo histórico; não é replay de execuções comprovadas na Clear.

## Protocolo e prevenção de uso de informações futuras

- Período fixado antes do cálculo: **02/01/2024–30/12/2025**. Aquecimento de indicadores em 2023.
- Universo fixo de **953 tickers** negociados na B3 em 2023, inclusive símbolos que depois deixaram de negociar. Não se consultam preços atuais para selecionar ativos ou viabilidade financeira.
- Preços OHLC brutos do COTAHIST B3, sem retroajuste por dividendos ou eventos futuros. Sinais só recebem o prefixo disponível até o fechamento daquele dia. O sinal anterior ao primeiro dia também é considerado.
- Janela de 120 pregões, bandas logarítmicas ±2σ, SMA200, SMA50 crescente e recuperação sobre a máxima anterior: mesmas funções `signal` e `plan` da versão já implementada. Não houve otimização de parâmetros nem procura de melhor período.
- Exigem-se 200 sessões consecutivas com dados para cada símbolo; não se preenchem buracos de papéis ilíquidos. Desempate entre sinais elegíveis: ordem alfabética, fixada previamente.
- Capital virtual R$ 500, teto aplicado R$ 450, risco planejado R$ 2,50 e uma posição por vez. Caixa ocioso sem remuneração. O bloqueio de −R$ 20 não reinicia no ano seguinte.
- O protocolo está em `config/backtest.protocol.json`; hash do protocolo, dados e código consta de `result.json`. Fontes e SHA-256 dos arquivos baixados ficam em `data/sources.json`.
- Essa disciplina evita antecipação de candles e seleção pelos resultados de 2026, mas não transforma os dados em um arquivo perfeito de tudo que se sabia à época. As limitações de cobertura e eventos abaixo permanecem.

## Comparação do mesmo capital inicial

| Estratégia/referência | Valor final | Variação acumulada |
| --- | ---: | ---: |
| Estratégia após custos¹ | R$ 479,55 | -4,09% |
| CDB 100% CDI bruto | R$ 632,52 | 26,50% |
| CDB 100% CDI líquido² | R$ 612,64 | 22,53% |
| Ibovespa (índice) | R$ 600,38 | 20,08% |
| Reposição pelo IPCA³ | R$ 546,51 | 9,30% |

¹ Estratégia após taxas estimadas e slippage, **antes de IR**. Não foi presumida remuneração do dinheiro parado. O valor final inclui R$ 1,36 de direitos a proventos, tratados como recebíveis não reinvestíveis por falta das datas de pagamento na fonte.
² CDB **hipotético** pagando 100% do CDI, sem taxa de administração, mantido até o final. CDI diário composto, SGS 12/BCB. Prazo superior a 720 dias: IR de 15% apenas sobre o rendimento. Não representa uma oferta de CDB disponível ao usuário. Não há IOF no resgate final; a curva exibida é a do CDB bruto.
³ IPCA mensal, SGS 433/BCB: inflação de janeiro/2024 a dezembro/2025. Não é rentabilidade de um investimento; é o valor para preservar o poder de compra de R$ 500. Como não existe IPCA diário, o último dia do teste é comparado aos meses completos correspondentes; isso não dá precisão diária de inflação.
Ibovespa: índice `IBOV` obtido no MT5, com base no último fechamento anterior ao período (**2023-12-28**, 134.185 pontos). É comparação teórica com o índice, sem custos de ETF e sem presumir que R$ 500 comprariam diretamente o índice.
Retorno real estimado da estratégia descontando o IPCA: **-12,25%**. Diferença em relação ao CDB líquido: **R$ 133,08 a menos**.

## Operações e controle de risco

- Operações encerradas: **14**; vencedoras: **2**; taxa de acerto: **14,29%**.
- Resultado das compras e vendas após custos: **R$ -21,81**; proventos: **R$ 1,36**.
- Custos totais estimados: **R$ 2,34**. Hipótese fixada: 0,05% por ponta + R$ 0,05 por execução; stop com dois ticks de reserva total de spread/slippage. Não é tarifário confirmado da Clear.
- Maior queda desde um pico da carteira, com marcação diária: **-4,38%**; fator de lucro: **0,30**.
- Bloqueio por perda acumulada acionado em **03/02/2025**. Depois disso não houve novas entradas, inclusive no restante de 2025. Não foi inventada uma revisão para reativá-la.
- Tempo com posição ao fim das sessões: **38,52%**; aplicação média marcada no período: aproximadamente **R$ 16,38**. O risco de R$ 2,50 e os lotes restringem muito o capital efetivamente investido.
- As 29 tentativas de entrada produziram 14 compras modeladas, 11 expirações sem gatilho e quatro cancelamentos por gap acima do preço máximo. Não há posição aberta no final.
- O pior negócio perdeu mais que R$ 2,50 por gap. Esse valor é risco planejado, não teto de perda garantido.

| Compra | Venda | Ativo histórico | Quantidade | Entrada modelada | Saída modelada | Resultado após custos | Saída |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 2024-01-24 | 2024-03-08 | BBOV11 | 1 | R$ 66,76 | R$ 64,83 | R$ -2,10 | stop |
| 2024-03-11 | 2024-03-20 | BREW11 | 1 | R$ 121,36 | R$ 113,35 | R$ -8,23 | gap_stop |
| 2024-03-22 | 2024-03-25 | ALUG11 | 2 | R$ 35,17 | R$ 34,15 | R$ -2,21 | stop |
| 2024-03-26 | 2024-04-09 | HSLG11 | 1 | R$ 97,87 | R$ 95,86 | R$ -2,21 | stop |
| 2024-04-29 | 2024-05-02 | JFLL11 | 1 | R$ 75,90 | R$ 74,42 | R$ -1,66 | stop |
| 2024-05-07 | 2024-08-05 | CRPT11 | 1 | R$ 13,67 | R$ 11,54 | R$ -2,24 | gap_stop |
| 2024-08-14 | 2024-10-11 | GENB11 | 2 | R$ 14,79 | R$ 17,40 | R$ 5,09 | target |
| 2024-10-15 | 2024-10-23 | BBOV11 | 1 | R$ 68,31 | R$ 67,12 | R$ -1,36 | stop |
| 2024-10-24 | 2024-11-04 | ALUG11 | 2 | R$ 45,59 | R$ 44,56 | R$ -2,25 | stop |
| 2024-11-07 | 2024-11-08 | DIVO11 | 1 | R$ 95,46 | R$ 93,33 | R$ -2,32 | stop |
| 2024-11-12 | 2024-11-18 | BMMT11 | 1 | R$ 119,64 | R$ 118,21 | R$ -1,65 | gap_stop |
| 2024-11-21 | 2024-11-28 | ALUG11 | 1 | R$ 45,47 | R$ 49,80 | R$ 4,18 | target |
| 2024-12-26 | 2025-01-03 | XINA11 | 5 | R$ 7,53 | R$ 7,16 | R$ -1,99 | stop |
| 2025-01-15 | 2025-02-03 | QDFI11 | 2 | R$ 6,25 | R$ 4,87 | R$ -2,87 | gap_stop |

## Execução histórica: o que foi e não foi demonstrado

O teste principal usa candles diários. A compra é modelada no **preço máximo**, somente na sessão seguinte ao sinal. Gap de abertura acima do teto cancela. Se a mínima puder atingir o stop antes do gatilho, a versão conservadora cancela; stop e alvo tocados no mesmo D1 são resolvidos pelo stop primeiro. Stops em gap usam a abertura menos dois ticks; alvos são fixos. Alvo no próprio dia da compra não é creditado se a ordem cronológica não puder ser demonstrada.
Uma segunda execução, fixada previamente com ordem intradiária favorável nos casos ambíguos, resultou no mesmo saldo: **R$ 479,55**. Não houve casos de desempate de stop/gatilho ou stop/alvo nas operações selecionadas. Isso **não é um intervalo estatístico nem garantia de execução**; filas, spread, leilões e ausência de contraparte continuam sem solução pelo D1.
Foi sondado histórico M1 da primeira entrada: 16 candles de negócios foram devolvidos para BBOV11 em 24/01/2024. Isso mostra cobertura intradiária parcial de um ativo, mas não oferece bid/ask, fila nem prova de execução em todos os 29 pedidos. O resultado principal não foi alterado por essa amostra e não deve ser chamado de replay tick a tick.
A validade na sessão seguinte é modelada por data. O COTAHIST não identifica se uma máxima ocorreu no contínuo, no leilão ou após o horário de cancelamento; portanto não foi possível reproduzir fielmente a expiração às 17h54 e os horários históricos por produto em todas as sessões. O backtest não valida a proteção real da Clear nem a persistência overnight. A execução de toda a quantidade é uma hipótese, não comprovação de liquidez.

## Eventos, lotes e limites de cobertura

O lote histórico é modelado pela classe no arquivo da época: ações/units 100; BDI12 ou especificação CI, uma cota; tick R$ 0,01. Isso evita usar o cadastro atual para escolher oportunidades, mas não é prova de todas as condições que a Clear aceitava em 2024–2025. O mercado fracionário de ações foi excluído.
Os eventos ex-data vêm de uma fonte secundária, Yahoo Finance, consultada apenas para datas até 2025. Nenhum preço ajustado dessa fonte é usado. Proventos são reconhecidos somente se a posição já existia antes da sessão ex; uma nova entrada é cancelada em ex-data. Splits conhecidos exigem novo aquecimento de 200 sessões; se ocorrerem durante uma posição, a conversão preserva a quantidade e os níveis econômicos. Datas de anúncio e pagamento, amortizações, subscrições e notícias históricas não foram integralmente reconstruídas. Não há filtro subjetivo de notícias escolhido retrospectivamente.
A fonte secundária não cobre todos os ativos; **52 sinais com plano financeiro admissível foram excluídos por indisponibilidade de eventos**. Isso deixa possível viés de cobertura, embora o universo de preços inclua deslistados. Os dados não demonstram ausência de todos os vieses de sobrevivência/eventos.
Os custos reais, impostos por tipo de instrumento e situação tributária pessoal não foram integralmente reproduzidos. A estratégia está apresentada antes de IR; o CDB bruto é a comparação no mesmo nível tributário. O CDB líquido é adicional. Proventos podem ter tratamento tributário específico.

## Auditoria reproduzível

Foram executados **nove testes específicos do backtest**, incluindo leitura apenas de prefixos conhecidos, alteração de dados futuros sem mudar sinais passados, sinal anterior ao primeiro pregão, gaps, lotes históricos e desempates conservadores. Os 29 testes anteriores do motor paper também permanecem disponíveis.
Arquivos: `result.json` (curvas, negócios, tentativas e hipóteses), `signals.json` (snapshots causais e motivos de rejeição), `summary.json` (resumo), `comparison.html` (comparativo), `data/sources.json` (proveniência) e `intraday.audit.json` (sondagem M1). Não houve otimização após observar o resultado.
Reprodução, a partir da raiz do projeto:
```powershell
py -3.13 tools/collect_backtest.py
py -3.13 tools/prepare_backtest.py
py -3.13 tools/collect_backtest_benchmark.py
py -3.13 tools/test_backtest.py
py -3.13 tools/backtest_swing.py
py -3.13 tools/report_backtest.py
```

Fontes: [COTAHIST B3](https://bvmf.bmfbovespa.com.br/pt-br/cotacoes-historicas/FormSeriesHistoricas.asp), [CDI SGS 12](https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial=02/01/2024&dataFinal=30/12/2025), [IPCA SGS 433](https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=01/01/2024&dataFinal=31/12/2025), [IR de renda fixa, Receita Federal](https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494).

**Conclusão:** neste período e sob as hipóteses fixadas, a estratégia perdeu capital e poder de compra e ficou abaixo do CDB e do Ibovespa. O teste não sustenta ativá-la com dinheiro real. Uma amostra de 14 negócios e as limitações de execução/eventos não permitem afirmar rentabilidade futura — nem positividade, nem perda certa em qualquer outro período.
