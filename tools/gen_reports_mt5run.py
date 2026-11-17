import json, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
d = json.load(open(R / 'reports/mt5run/results.json')); res = d['results']; B = d['bench']
OOS = 'fora_da_amostra(2025..2026-11-16)'; DEV = 'desenvolvimento(2021-11..2023)'; VAL = 'validacao(2024)'


def f(x, suf=''):
    return 'n/d' if x is None else f'{x}{suf}'


def mrow(name, m):
    return (f"| {name} | {m.get('n_trades')} | {f(m.get('ret_pct'),'%')} | {f(m.get('ann_pct'),'%')} | {f(m.get('max_dd_pct'),'%')} | "
            f"{f(m.get('profit_factor'))} | {f(m.get('hit_rate'),'%')} | {f(m.get('avg_win'))} | {f(m.get('avg_loss'))} | {f(m.get('expectancy'))} | {f(m.get('avg_hold_days'))} | {f(m.get('costs'))} |")


HDR = ("| Janela | Ops | Retorno | Anualiz. | DD máx | PF | Acerto | Lucro méd (R$) | Prej. méd (R$) | Expectativa (R$/op) | Dias méd. | Custos (R$) |\n"
       "|---|---|---|---|---|---|---|---|---|---|---|---|")
NOTE = ("> **Aviso metodológico central.** Isto **não** é um relatório do Strategy Tester do MT5. O servidor da Clear não oferece símbolos fracionários (sufixo F); "
        "os EAs recusam rodar nos lotes disponíveis (ver `Carteira_Consolidada.md`). Os números abaixo vêm de um simulador Python (`tools/sim_swing_portfolio.py`) "
        "que porta a lógica dos EAs sobre candles D1 reais lidos do MT5, com ações inteiras. Não autoriza negociação real.\n")


def strat_md(s, title, desc, cls, why):
    r = res[s]; y = r['years']
    t = [f"# {title}\n", NOTE, f"## Lógica\n{desc}\n", "## Classificação\n", f"**{cls}**\n\n{why}\n",
         "## Métricas (carteira consolidada, R$ 500, até 3 posições)\n", HDR,
         mrow('Período total (2021-11-17 a 2026-11-16)', r['total']), mrow('Desenvolvimento 2021-11 a 2023', r[DEV]),
         mrow('Validação 2024', r[VAL]), mrow('Fora da amostra 2025 a 16/11/2026', r[OOS]), "",
         f"Capital final: R$ {r['total']['end']} (variação de equity R$ {r['total']['pnl_eq']}); lucro líquido das operações fechadas R$ {r['total']['net_trades']}; custos totais R$ {r['total']['costs']}.", "",
         "Retorno por ano (equity): " + ', '.join(f"{k}: {v}%" for k, v in y.items()) + " (2021 sem operações: dados começam em 17/11/2021).", "",
         "## Comparação com benchmarks (retorno do período, sem custos/impostos)\n",
         "| Janela | Estratégia | IBOV (preço) | BOVA11 | CDI |\n|---|---|---|---|---|"]
    for k, name in ((DEV, 'Desenvolvimento'), (VAL, '2024'), (OOS, 'Fora da amostra')):
        t.append(f"| {name} | {r[k]['ret_pct']}% | {B['IBOV'][k]}% | {B['BOVA11'][k]}% | {B['CDI'][k]}% |")
    t.append(f"| Total | {r['total']['ret_pct']}% | {B['IBOV']['total']}% | {B['BOVA11']['total']}% | {B['CDI']['total']}% |")
    t += ["", "Nenhuma das duas bateu o CDI em janela alguma; frente ao IBOV só superaram em 2024, ano de queda do índice.", "",
          "## Estatística\n",
          f"Intervalo bootstrap 95% da expectativa por operação (R$): {r['bootstrap95_expectancy']} — inclui zero; **sem evidência estatística de vantagem**. "
          f"Amostra: {r['total']['n_trades']} operações, autocorrelacionadas entre ativos; o bootstrap simples ignora isso.", "",
          f"Concentração: lucro líquido R$ {r['concentration']['net']}; as 3 maiores operações somam R$ {r['concentration']['top3']}; sem elas o resultado é R$ {r['concentration']['net_without_top3']}.", "",
          f"Regime: meses de queda do IBOV ({r['regime']['meses_ibov_queda']}): retorno médio mensal {r['regime']['ret_medio_nesses_%']}%; meses de alta ({r['regime']['meses_ibov_alta']}): {r['regime']['ret_medio_nesses_alta_%']}%.", "",
          f"Posições abertas ao fim: {r['open_at_end'] or 'nenhuma'}. Suspensão de 10% acionada: {'sim' if r['suspended'] else 'não'}. O drawdown máximo ficou abaixo do limite preventivo de 6%.", ""]
    return '\n'.join(t)


A_desc = "Regressão linear de ln(close) em 120 pregões; inclinação > 0; fechamento > SMA200; SMA50 > SMA50 de 20 pregões atrás e > SMA200; toque na zona inferior (30% inferiores do canal ±2σ) em D-1 ou D-2; fechamento acima da máxima anterior e do limite inferior. Stop inicial 2×ATR(14); stop móvel = máxima desde a entrada − 2×ATR; saída por perda de tendência (inclinação ≤ 0, fechamento < SMA200 ou SMA50 < SMA200)."
B_desc = "Fechamento de D-1 acima da máxima dos 20 pregões anteriores, volume de D-1 acima da média de 20, retorno de 60 pregões maior que o do IBOV. Stop inicial 2×ATR(14); stop móvel = máx(mínima de 10 pregões, preço − 2×ATR) quando em lucro; saída se fechamento < mínima dos 10 pregões anteriores."
A_why = ('Retorno líquido positivo mas irrisório (+2,65% em ~5 anos contra CDI +82,8%); fora da amostra +1,96%, PF 1,52, mas a amostra é pequena (29 ops), '
         'o IC95% da expectativa inclui zero, as 3 maiores operações superam todo o lucro e custos 2× tornam o total negativo. Não é reprovada '
         '(sem prejuízo persistente, risco controlado), mas não há evidência para paper trading.')
B_why = ('Retorno +3,06% no total, mas só +0,21% fora da amostra (PF 1,03, DD −3,67%); negativa em 2024 e 2026; com custos 2× + slippage 3× o fora da amostra é negativo; '
         'com apenas 1 posição o total é −0,56%. Sem evidência estatística.')
(R / 'reports/Backtest_Estrategia_A.md').write_text(strat_md('A', 'Backtest – Estratégia A (reversão em canal de alta)', A_desc, 'REVISÃO NECESSÁRIA', A_why), encoding='utf-8')
(R / 'reports/Backtest_Estrategia_B.md').write_text(strat_md('B', 'Backtest – Estratégia B (rompimento de 20 pregões)', B_desc, 'REVISÃO NECESSÁRIA (próxima de reprovada)', B_why), encoding='utf-8')

L = ["# Análise de Robustez\n", NOTE,
     "Parâmetros dos EAs mantidos como estavam. As variações abaixo **só reportam sensibilidade**; nada foi escolhido a partir delas nem otimizado.\n"]
for s in 'AB':
    r = res[s]
    L += [f"## Estratégia {s}\n", "### Custos e slippage (carteira)\n", "| Cenário | Retorno total | Fora da amostra | DD máx | Ops |\n|---|---|---|---|---|",
          f"| Base (0,05%/lado + R$0,05; slip 1 tick entrada, 2 ticks stop) | {r['total']['ret_pct']}% | {r[OOS]['ret_pct']}% | {r['total']['max_dd_pct']}% | {r['total']['n_trades']} |"]
    for k, v in r['robust_costs'].items():
        L.append(f"| {k} | {v['total']}% | {v[OOS]}% | {v['mdd']}% | {v['n']} |")
    L += ["", "### Sensibilidade de parâmetros\n", "| Parâmetro | Retorno total | Fora da amostra | DD | Ops | PF |\n|---|---|---|---|---|---|"]
    for v in r['sensitivity']:
        L.append(f"| {v['param']} | {v['ret_pct']}% | {v['oos_ret']}% | {v['mdd']}% | {v['n']} | {f(v['pf'])} |")
    L += ["", "### Dependência por ativo (standalone R$ 500, 1 posição) e leave-one-out (carteira)\n",
          "| Ativo | Standalone total | Standalone OOS | Ops | PF | Carteira sem o ativo |\n|---|---|---|---|---|---|"]
    for a, v in r['solo_assets'].items():
        L.append(f"| {a} | {v['ret_pct']}% | {v['oos_ret']}% | {v['n']} | {f(v['pf'])} | {r['leave_one_out'][a]['ret_pct']}% |")
    L += ["", f"Concentração: {r['concentration']}", "", f"Regimes: {r['regime']}", "", f"Bootstrap 95% da expectativa/op (R$): {r['bootstrap95_expectancy']}", ""]
L += ["## Walk-forward\n",
      "Não executado como otimização: as estratégias têm parâmetros fixos e **nenhum foi otimizado**, então não há etapa de ajuste a validar. Os resultados por ano e por janela (desenvolvimento/validação/fora da amostra) fazem o papel de avaliação sequencial; as janelas são curtas e 2021 não tem operações. Não há significância estatística demonstrável.\n",
      "## Limitações\n",
      "- O histórico MT5 começa em 16–17/11/2021; a estratégia A precisa de 200 pregões de aquecimento (primeiros sinais só em ~set/2022), logo a janela de desenvolvimento é efetivamente curta.",
      "- Candles D1 do MT5 sem ajuste comprovado a proventos/eventos; gaps de −26% a −33% em 26/10/2026 (BBAS3, BBDC4, BOVA11), −28,6% em 27/11/2025 (EGIE3) e +16% em 27/06/2024 (SUZB3) sugerem eventos corporativos. Nenhuma operação simulada nesses ativos atravessou esses gaps, mas outras distorções não são descartáveis.",
      "- Universo fixo de 10 ações líquidas de hoje: viés de sobrevivência; sem ativos deslistados.",
      "- Custos (0,05%/lado + R$ 0,05) são premissa dos EAs, não tarifa documentada da Clear; o fracionário real tem spread/liquidez piores.",
      "- Execução diária com abertura do dia seguinte e stop intradiário pela mínima; sem ticks. Gap de stop é preenchido na abertura.",
      "- Risco agregado: cada posição ≤ R$ 2,50 (0,5%), soma das posições abertas ≤ R$ 7,50 (1,5%); ordem de entrada fixa pela lista de ativos (sem ranking).", ""]
(R / 'reports/Analise_Robustez.md').write_text('\n'.join(L), encoding='utf-8')

dd = d['data']
C = ["# Carteira Consolidada e Viabilidade no MT5\n", NOTE, "## O que foi verificado no MT5/Clear\n",
     "- Compilação: `B3Swing_A_UptrendPullback.mq5` e `B3Swing_B_20DayBreakout.mq5` compilam com 0 erros e 0 avisos (MetaEditor build 6230). Compilar não é backtest aprovado.",
     "- Símbolos fracionários: **ITUB4F, BBAS3F, WEGE3F, GGBR4F, PETR4F, VALE3F, BBDC4F, ABEV3F, EGIE3F, SUZB3F não existem** no servidor (0 símbolos terminados em F entre 3.004 listados). Existem as variantes `X`, `XM` e `XQ`; ITUB4 tem lote mínimo 100; ITUB4M/ITUB4Q têm lote mínimo 142.000.",
     "- Strategy Tester: rodou (config em `reports/mt5run/tester/B3_A_ITUB4.ini`), mas o EA A parou em OnInit com `Simbolo nao habilita lote fracionario de ate uma acao por volume minimo` — comportamento correto do EA, não um bug. Nenhum relatório do Tester foi gerado. O EA B não foi executado no Tester, pois usa a mesma verificação de lote.",
     "- Com R$ 500, 100 ações de ITUB4 são inviáveis, e o teste nos lotes padrão exigiria alterar a regra de lote do EA (não alterei).",
     "- Histórico disponível: D1 de 16–17/11/2021 a 16/11/2026 (1.248 barras por ativo). O período 01/01–16/11/2021 **não existe** no servidor. Ajuste a proventos: não comprovado.",
     "- Limitação do MT5: um EA opera um símbolo por teste; uma carteira com R$ 500 compartilhados não é reproduzível no Tester sem EA multiativo (não existe). A consolidação foi feita em simulador externo.",
     "\n## Carteira consolidada (simulador Python, não MT5)\n",
     "Capital compartilhado R$ 500; ações inteiras; máx. 3 posições; risco ≤ R$ 2,50/op e ≤ R$ 7,50 agregado; custos 0,05%/lado + R$ 0,05; travas de 6% (sem novas entradas) e 10% (fecha tudo, suspende); só compra, sem alavancagem.\n",
     HDR]
for s in 'AB':
    C += [mrow(f'{s} total', res[s]['total']), mrow(f'{s} fora da amostra', res[s][OOS])]
C += ["", "Variante com 1 posição: " + '; '.join(f"{s}: total {res[s]['max_pos_1']['total']['ret_pct']}%, OOS {res[s]['max_pos_1'][OOS]['ret_pct']}%" for s in 'AB'), "",
      "## Cobertura de dados\n", "| Ativo | Início | Barras | Gaps >15% |\n|---|---|---|---|"]
for a, v in dd.items():
    C.append(f"| {a} | {v['first']} | {v['bars']} | {v['gaps_gt15pct'] or '-'} |")
(R / 'reports/Carteira_Consolidada.md').write_text('\n'.join(C) + '\n', encoding='utf-8')

cmp = ["# Comparativo das Estratégias A e B\n", NOTE, "| Métrica | A | B |\n|---|---|---|"]
rows = [('Retorno total', 'ret_pct', '%'), ('Anualizado', 'ann_pct', '%'), ('DD máx', 'max_dd_pct', '%'), ('Profit factor', 'profit_factor', ''),
        ('Acerto', 'hit_rate', '%'), ('Operações', 'n_trades', ''), ('Expectativa R$/op', 'expectancy', ''), ('Custos R$', 'costs', '')]
for n, k, u in rows:
    cmp.append(f"| {n} | {f(res['A']['total'].get(k),u)} | {f(res['B']['total'].get(k),u)} |")
for n, k, u in [('OOS retorno', 'ret_pct', '%'), ('OOS DD', 'max_dd_pct', '%'), ('OOS PF', 'profit_factor', ''), ('OOS ops', 'n_trades', '')]:
    cmp.append(f"| {n} | {f(res['A'][OOS].get(k),u)} | {f(res['B'][OOS].get(k),u)} |")
cmp += [f"| IBOV / BOVA11 / CDI (total) | {B['IBOV']['total']}% / {B['BOVA11']['total']}% / {B['CDI']['total']}% | idem |", "",
        "**Melhor ajustada ao risco: A**, por pequena margem (OOS +1,96% vs +0,21%, PF 1,52 vs 1,03, DD OOS −2,1% vs −3,7%), mas sem significância (IC95% da expectativa inclui zero em ambas), dependente de 3 operações e negativa no total com custos 2×. Nenhuma bate CDI/IBOV. Ambas: REVISÃO NECESSÁRIA; nenhuma foi aprovada para paper trading.", "",
        "Detalhes: `Backtest_Estrategia_A.md`, `Backtest_Estrategia_B.md`, `Analise_Robustez.md`, `Carteira_Consolidada.md`. O estudo Python anterior (2024–2025) permanece em `reports/backtest/`.", ""]
(R / 'reports/Comparativo_Estrategias.md').write_text('\n'.join(cmp), encoding='utf-8')
(R / 'reports/Resumo Para ChatGPT.md').write_text(
    "# Resumo Para ChatGPT\n\n" + NOTE + "\n" + '\n'.join(cmp[2:]) +
    "\n## Executado\n- Compilação dos 2 EAs; verificação de símbolos e lotes; tentativa real no Strategy Tester (falhou por lote, documentada); coleta D1 de 10 ações + IBOV + BOVA11; CDI (SGS 12, BCB); simulação consolidada, custos/slippage, sensibilidade, leave-one-out, concentração, regimes.\n"
    "## Não executado\n- Backtest MT5 dos EAs (sem símbolo fracionário na Clear); janela 01/01–16/11/2021 (sem dados); otimização/walk-forward formal (nada foi otimizado); ajuste comprovado de proventos.\n"
    "## Correções de código\n- Nenhuma alteração nos EAs.\n", encoding='utf-8')
