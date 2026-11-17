# Carteira Consolidada e Viabilidade no MT5

> **Aviso metodológico central.** Isto **não** é um relatório do Strategy Tester do MT5. O servidor da Clear não oferece símbolos fracionários (sufixo F); os EAs recusam rodar nos lotes disponíveis (ver `Carteira_Consolidada.md`). Os números abaixo vêm de um simulador Python (`tools/sim_swing_portfolio.py`) que porta a lógica dos EAs sobre candles D1 reais lidos do MT5, com ações inteiras. Não autoriza negociação real.

## O que foi verificado no MT5/Clear

- Compilação: `B3Swing_A_UptrendPullback.mq5` e `B3Swing_B_20DayBreakout.mq5` compilam com 0 erros e 0 avisos (MetaEditor build 6230). Compilar não é backtest aprovado.
- Símbolos fracionários: **ITUB4F, BBAS3F, WEGE3F, GGBR4F, PETR4F, VALE3F, BBDC4F, ABEV3F, EGIE3F, SUZB3F não existem** no servidor (0 símbolos terminados em F entre 3.004 listados). Existem as variantes `X`, `XM` e `XQ`; ITUB4 tem lote mínimo 100; ITUB4M/ITUB4Q têm lote mínimo 142.000.
- Strategy Tester: rodou (config em `reports/mt5run/tester/B3_A_ITUB4.ini`), mas o EA A parou em OnInit com `Simbolo nao habilita lote fracionario de ate uma acao por volume minimo` — comportamento correto do EA, não um bug. Nenhum relatório do Tester foi gerado. O EA B não foi executado no Tester, pois usa a mesma verificação de lote.
- Com R$ 500, 100 ações de ITUB4 são inviáveis, e o teste nos lotes padrão exigiria alterar a regra de lote do EA (não alterei).
- Histórico disponível: D1 de 16–17/11/2021 a 16/11/2026 (1.248 barras por ativo). O período 01/01–16/11/2021 **não existe** no servidor. Ajuste a proventos: não comprovado.
- Limitação do MT5: um EA opera um símbolo por teste; uma carteira com R$ 500 compartilhados não é reproduzível no Tester sem EA multiativo (não existe). A consolidação foi feita em simulador externo.

## Carteira consolidada (simulador Python, não MT5)

Capital compartilhado R$ 500; ações inteiras; máx. 3 posições; risco ≤ R$ 2,50/op e ≤ R$ 7,50 agregado; custos 0,05%/lado + R$ 0,05; travas de 6% (sem novas entradas) e 10% (fecha tudo, suspende); só compra, sem alavancagem.

| Janela | Ops | Retorno | Anualiz. | DD máx | PF | Acerto | Lucro méd (R$) | Prej. méd (R$) | Expectativa (R$/op) | Dias méd. | Custos (R$) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A total | 87 | 2.65% | 0.52% | -3.68% | 1.2 | 37.9% | 2.459 | -1.25 | 0.157 | 14.6 | 12.22 |
| A fora da amostra | 29 | 1.96% | 1.04% | -2.12% | 1.52 | 44.8% | 2.309 | -1.233 | 0.355 | 15.6 | 4.0 |
| B total | 124 | 3.06% | 0.61% | -3.9% | 1.15 | 39.5% | 2.371 | -1.345 | 0.124 | 17.3 | 17.32 |
| B fora da amostra | 44 | 0.21% | 0.11% | -3.67% | 1.03 | 31.8% | 2.822 | -1.281 | 0.024 | 17.5 | 6.13 |

Variante com 1 posição: A: total 1.26%, OOS 0.92%; B: total -0.56%, OOS -0.6%

## Cobertura de dados

| Ativo | Início | Barras | Gaps >15% |
|---|---|---|---|
| ITUB4 | 2021-11-17 | 1248 | - |
| BBAS3 | 2021-11-17 | 1248 | [['2026-10-26', -33.3]] |
| WEGE3 | 2021-11-17 | 1248 | - |
| GGBR4 | 2021-11-16 | 1249 | - |
| PETR4 | 2021-11-17 | 1248 | - |
| VALE3 | 2021-11-17 | 1248 | - |
| BBDC4 | 2021-11-17 | 1248 | [['2026-10-26', -26.2]] |
| ABEV3 | 2021-11-17 | 1248 | - |
| EGIE3 | 2021-11-17 | 1248 | [['2025-11-27', -28.6]] |
| SUZB3 | 2021-11-17 | 1248 | [['2024-06-27', 16.3]] |
| IBOV | 2021-11-17 | 1248 | - |
| BOVA11 | 2021-11-17 | 1248 | [['2026-10-26', -30.6]] |
