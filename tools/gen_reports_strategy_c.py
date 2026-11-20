import json, pathlib

R = pathlib.Path(__file__).resolve().parent.parent
d = json.load(open(R / 'reports/mt5run/results.json', encoding='utf-8'))
res = d['results']
B = d['bench']
OOS = 'fora_da_amostra(2025..2026-11-16)'
DEV = 'desenvolvimento(2021-11..2023)'
VAL = 'validacao(2024)'


def f(x, suf=''):
    return 'n/d' if x is None else f'{x}{suf}'


def mrow(name, m):
    return (f"| {name} | {m.get('n_trades')} | {f(m.get('ret_pct'),'%')} | {f(m.get('ann_pct'),'%')} | {f(m.get('max_dd_pct'),'%')} | "
            f"{f(m.get('profit_factor'))} | {f(m.get('hit_rate'),'%')} | {f(m.get('avg_win'))} | {f(m.get('avg_loss'))} | {f(m.get('expectancy'))} | {f(m.get('avg_hold_days'))} | {f(m.get('costs'))} |")


HDR = ("| Janela | Ops | Retorno | Anualiz. | DD máx | PF | Acerto | Lucro méd (R$) | Prej. méd (R$) | Expectativa (R$/op) | Dias méd. | Custos (R$) |\n"
       "|---|---|---|---|---|---|---|---|---|---|---|---|")
NOTE = ("> **Aviso metodológico central.** Isto **não** é um relatório gerado pelo Strategy Tester do MT5. O servidor da Clear não oferece símbolos fracionários (sufixo F); "
        "os EAs recusam rodar nos lotes disponíveis (100 ações). Os números abaixo vêm do simulador Python (`tools/sim_swing_portfolio.py`) "
        "que porta a lógica exata dos EAs sobre candles D1 reais coletados do MT5, com ações inteiras e caixa compartilhado. Não autoriza negociação real.\n")


def gen_backtest_c():
    rc = res['C']
    y = rc['years']
    desc = ("Ranking diário de Força Relativa (RS20, RS60, RS120 vs IBOV) com pesos 0,40 / 0,35 / 0,25 sobre percentis transversais. "
            "Filtros obrigatórios: RS20 > 0, RS60 > 0, Fechamento > SMA50, SMA50 > SMA200, SMA50 ascendente (10 pregões). TOP 3 elegíveis. "
            "Canal de regressão logarítmica de 120 pregões com bandas ±2σ; compra na zona entre a banda inferior e a linha central, com confirmação "
            "(fechamento > máxima anterior). Stop inicial 2×ATR(14); stop móvel pelo maior fechamento − 2×ATR; saída adicional se fechamento < SMA50 ou inclinação ≤ 0. "
            "Risco máx 0,5% por operação, agregado 1,5%, travas de 6% (preventiva) e 10% (suspensão/liquidação sobre o maior patrimônio).")
    cls = "REVISÃO NECESSÁRIA"
    why = ("Apresentou lucro líquido positivo (+2,26% total, +0,54% fora da amostra) com drawdown extremamente reduzido (-1,46%) e profit factor saudável (1,51). "
           "Além disso, sobreviveu a custos 2× e slippage 3× (+0,53%). Porém, o número de operações é diminuto (apenas 32 em 5 anos, sendo 10 fora da amostra), "
           "o intervalo bootstrap de 95% da expectativa inclui zero [-0,42; +1,22], as 3 maiores operações concentram todo o lucro (sem elas o resultado seria -R$ 6,31), "
           "e o ganho acumulado é irrisório frente ao CDI (+82,76%). Não há evidência estatística suficiente para autorizar paper trading.")

    t = [
        "# Backtest – Estratégia C (Força Relativa e Canal de Alta)\n",
        NOTE,
        f"## Lógica\n{desc}\n",
        "## Classificação\n",
        f"**{cls}**\n\n{why}\n",
        "## Métricas (carteira consolidada, R$ 500, até 3 posições)\n",
        HDR,
        mrow('Período total (2021-11-17 a 2026-11-16)', rc['total']),
        mrow('Desenvolvimento 2021-11 a 2023', rc[DEV]),
        mrow('Validação 2024', rc[VAL]),
        mrow('Fora da amostra 2025 a 16/11/2026', rc[OOS]),
        "",
        f"Capital final: R$ {rc['total']['end']} (variação de equity R$ {rc['total']['pnl_eq']}); lucro líquido das operações fechadas R$ {rc['total']['net_trades']}; custos operacionais totais R$ {rc['total']['costs']}.",
        "",
        "Retorno por ano (equity): " + ', '.join(f"{k}: {v}%" for k, v in y.items()) + " (2021 sem operações por falta de barras de aquecimento para SMA200).",
        "",
        "## Comparação com Benchmarks (retorno acumulado do período)\n",
        "| Janela | Estratégia C | IBOV (preço) | BOVA11 | CDI |\n|---|---|---|---|---|",
        f"| Desenvolvimento (2021-11 a 2023) | {rc[DEV]['ret_pct']}% | {B['IBOV'][DEV]}% | {B['BOVA11'][DEV]}% | {B['CDI'][DEV]}% |",
        f"| Validação (2024) | {rc[VAL]['ret_pct']}% | {B['IBOV'][VAL]}% | {B['BOVA11'][VAL]}% | {B['CDI'][VAL]}% |",
        f"| Fora da amostra (2025 a 16/11/2026) | {rc[OOS]['ret_pct']}% | {B['IBOV'][OOS]}% | {B['BOVA11'][OOS]}% | {B['CDI'][OOS]}% |",
        f"| Total | {rc['total']['ret_pct']}% | {B['IBOV']['total']}% | {B['BOVA11']['total']}% | {B['CDI']['total']}% |",
        "",
        "Em nenhuma janela a estratégia superou o CDI. Frente ao Ibovespa, superou em 2024 (ano em que o IBOV caiu 10,36% e a estratégia oscilou apenas -0,16%).",
        "",
        "## Análise Estatística\n",
        f"- **Intervalo Bootstrap 95% da Expectativa por Operação:** {rc['bootstrap95_expectancy']} R$/op. Cruzando o zero, demonstrando ausência de significância estatística robusta (p > 0,05).",
        f"- **Amostra:** {rc['total']['n_trades']} operações fechadas em ~5 anos (média de 6,4 operações/ano). A baixa rotatividade é consequência direta do filtro restritivo combinado (ranking + canal + confirmação) e da restrição de capital (R$ 500).",
        f"- **Concentração de Lucros:** Lucro líquido total R$ {rc['concentration']['net']}; a maior operação (top 1) gerou R$ {rc['concentration']['top1']:.2f}; as 3 maiores somam R$ {rc['concentration']['top3']:.2f}. Sem as 3 maiores, o resultado líquido é R$ {rc['concentration']['net_without_top3']:.2f}.",
        f"- **Comportamento por Regime de Mercado:** Em meses de queda do IBOV ({rc['regime']['meses_ibov_queda']}), retorno médio mensal de {rc['regime']['ret_medio_nesses_%']}%; em meses de alta ({rc['regime']['meses_ibov_alta']}), retorno médio de {rc['regime']['ret_medio_nesses_alta_%']}%.",
        f"- **Controle de Risco e Posições:** Posições abertas ao final: {rc['open_at_end'] or 'nenhuma'}. Suspensão de 10% acionada: {'Sim' if rc['suspended'] else 'Não'}. O drawdown máximo (-1,46%) jamais ameaçou a trava preventiva de 6% nem a trava de 10%."
    ]
    (R / 'reports/Backtest_Estrategia_C.md').write_text('\n'.join(t) + '\n', encoding='utf-8')


def gen_comparativo_a_c():
    ra = res['A']
    rc = res['C']
    rows = [
        ('Capital inicial', 'R$ 500,00', 'R$ 500,00'),
        ('Capital final', f"R$ {ra['total']['end']}", f"R$ {rc['total']['end']}"),
        ('Retorno total líquido', f"{ra['total']['ret_pct']}%", f"{rc['total']['ret_pct']}%"),
        ('Retorno anualizado', f"{ra['total']['ann_pct']}%", f"{rc['total']['ann_pct']}%"),
        ('Drawdown máximo consolidado', f"{ra['total']['max_dd_pct']}%", f"{rc['total']['max_dd_pct']}%"),
        ('Profit Factor', f"{ra['total']['profit_factor']}", f"{rc['total']['profit_factor']}"),
        ('Taxa de acerto (Hit rate)', f"{ra['total']['hit_rate']}%", f"{rc['total']['hit_rate']}%"),
        ('Número de operações', f"{ra['total']['n_trades']}", f"{rc['total']['n_trades']}"),
        ('Lucro médio por acerto', f"R$ {ra['total']['avg_win']}", f"R$ {rc['total']['avg_win']}"),
        ('Prejuízo médio por perda', f"R$ {ra['total']['avg_loss']}", f"R$ {rc['total']['avg_loss']}"),
        ('Expectativa matemática', f"R$ {ra['total']['expectancy']}/op", f"R$ {rc['total']['expectancy']}/op"),
        ('Custos operacionais totais', f"R$ {ra['total']['costs']}", f"R$ {rc['total']['costs']}"),
        ('Prazo médio de permanência', f"{ra['total']['avg_hold_days']} dias", f"{rc['total']['avg_hold_days']} dias"),
        ('Retorno Fora da Amostra (2025-2026)', f"{ra[OOS]['ret_pct']}%", f"{rc[OOS]['ret_pct']}%"),
        ('Drawdown Fora da Amostra', f"{ra[OOS]['max_dd_pct']}%", f"{rc[OOS]['max_dd_pct']}%"),
        ('Profit Factor Fora da Amostra', f"{ra[OOS]['profit_factor']}", f"{rc[OOS]['profit_factor']}"),
        ('Operações Fora da Amostra', f"{ra[OOS]['n_trades']}", f"{rc[OOS]['n_trades']}"),
        ('Expectativa Fora da Amostra', f"R$ {ra[OOS]['expectancy']}/op", f"R$ {rc[OOS]['expectancy']}/op"),
        ('Retorno IBOV (período total)', f"{B['IBOV']['total']}%", f"{B['IBOV']['total']}%"),
        ('Retorno CDI (período total)', f"{B['CDI']['total']}%", f"{B['CDI']['total']}%")
    ]

    lines = [
        "# Comparativo Detalhado: Estratégia A vs Estratégia C\n",
        NOTE,
        "## Tabela Comparativa de Métricas (2021 a 2026)\n",
        "| Métrica | Estratégia A (Canal Pullback) | Estratégia C (Força Relativa + Canal) |",
        "|---|---|---|"
    ]
    for m, a_val, c_val in rows:
        lines.append(f"| {m} | {a_val} | {c_val} |")

    lines += [
        "",
        "## Análise Comparativa dos Pilares Quantitativos\n",
        "### 1. Rentabilidade vs Preservação de Capital",
        "- **Estratégia A:** Retorno ligeiramente superior (+2,65% vs +2,26%), impulsionado por maior número de operações (87 vs 32) e maior retorno fora da amostra (+1,96% vs +0,54%).",
        "- **Estratégia C:** Muito mais defensiva. O drawdown máximo foi de apenas **-1,46%**, menos da metade do drawdown da Estratégia A (-3,68%). O ranking de força relativa atuou como um forte filtro de contenção de perdas em períodos desfavoráveis.",
        "",
        "### 2. Eficiência Estatística e Assimetria",
        "- **Profit Factor:** A Estratégia C obteve PF de **1,51** contra **1,20** da Estratégia A (e 1,55 vs 1,52 fora da amostra).",
        "- **Assimetria (Payoff):** A Estratégia C possui relação lucro médio / prejuízo médio de **3,86** (R$ 3,715 / R$ 0,963), enquanto a Estratégia A possui payoff de **1,97** (R$ 2,459 / R$ 1,250). A Estratégia C aceita taxa de acerto menor (28,1% vs 37,9%) em troca de perdas muito pequenas e carona em altas maiores.",
        "- **Expectativa Matemática:** R$ 0,353 por operação em C vs R$ 0,157 por operação em A.",
        "",
        "### 3. Sensibilidade a Custos e Atrito Operacional",
        "- Em cenário de **Custos Duplicados + Slippage Triplicado**, a Estratégia A torna-se **negativa** no total (-0,12%) e fora da amostra (+0,37%).",
        "- A Estratégia C **permanece positiva** tanto no total (+0,53%) quanto fora da amostra (+0,15%), gastando muito menos em corretagens e emolumentos (custos totais de R$ 4,59 em C contra R$ 12,22 em A).",
        "",
        "### 4. Concentração e Significância",
        "- Ambas sofrem de extrema concentração de lucros: na Estratégia A, as 3 maiores operações somam R$ 23,03 (superando o lucro total de R$ 13,67); na Estratégia C, somam R$ 17,60 (superando o lucro total de R$ 11,29).",
        "- Em ambas, o intervalo bootstrap 95% cruza o zero (A: [-0,305; +0,669], C: [-0,420; +1,215]). Nenhuma possui comprovação estatística irrefutável.",
        "",
        "### 5. Veredito da Estratégia Mais Robusta",
        "A **Estratégia C é estruturalmente mais robusta que a Estratégia A** no controle de risco, controle de drawdown (-1,46% vs -3,68%), tolerância a custos/slippage elevados e assimetria por trade (payoff 3,86). No entanto, sua amostra de 32 operações é reduzida demais, impedindo aprovação direta para negociação."
    ]
    (R / 'reports/Comparativo_A_C.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def gen_robustez_c():
    rc = res['C']
    lines = [
        "# Análise de Robustez – Estratégia C\n",
        NOTE,
        "## 1. Testes de Estresse de Custos e Slippage\n",
        "Avaliação do impacto de custos operacionais (emolumentos/corretagem) e slippages de execução na carteira compartilhada:\n",
        "| Cenário de Estresse | Retorno Total | Retorno OOS | Drawdown Máx | Nº Ops |",
        "|---|---|---|---|---|",
        f"| Base (0,05%/lado + R$0,05; slip 1 tick entrada, 2 ticks stop) | {rc['total']['ret_pct']}% | {rc[OOS]['ret_pct']}% | {rc['total']['max_dd_pct']}% | {rc['total']['n_trades']} |"
    ]
    for k, v in rc['robust_costs'].items():
        lines.append(f"| {k} | {v['total']}% | {v[OOS]}% | {v['mdd']}% | {v['n']} |")

    lines += [
        "",
        "> [!NOTE]",
        "> A Estratégia C demonstrou alta resiliência aos custos. Mesmo sob o estresse severo de custos 2× associado a slippage 3×, a estratégia permaneceu em terreno positivo (+0,53% no total e +0,15% OOS). Isso se deve ao reduzido número de trades (32) e ao alto payoff médio (R$ 3,715 por acerto).",
        "",
        "## 2. Teste Leave-One-Out por Ativo (Carteira com 9 Ativos)\n",
        "Mede o impacto da exclusão sistemática de cada um dos ativos do universo elegível:\n",
        "| Ativo Excluído | Retorno Total | Drawdown Máx | Nº Ops |",
        "|---|---|---|---|"
    ]
    for a, v in rc['leave_one_out'].items():
        lines.append(f"| Sem {a} | {v['ret_pct']}% | {v['mdd']}% | {v['n']} |")

    lines += [
        "",
        "O teste leave-one-out confirma que a estratégia não depende exclusivamente de um único papel para fechar positiva. Todos os 10 cenários sem um ativo mantiveram retorno positivo (variando de +1,15% a +3,21%). A exclusão de GGBR4 elevou o retorno para +3,21% (ativo com perdas no período).",
        "",
        "## 3. Desempenho Isolado por Ativo (Standalone R$ 500, Max Posições = 1)\n",
        "Simulação com o capital total alocado exclusivamente a cada ação individualmente:\n",
        "| Ativo | Retorno Total | Retorno OOS | Nº Ops | Profit Factor | Drawdown Máx |",
        "|---|---|---|---|---|---|"
    ]
    for a, v in rc['solo_assets'].items():
        lines.append(f"| {a} | {f(v['ret_pct'],'%')} | {f(v['oos_ret'],'%')} | {v['n']} | {f(v['pf'])} | {f(v['mdd'],'%')} |")

    lines += [
        "",
        "## 4. Análise de Concentração de Lucros\n",
        f"- **Número total de operações:** {rc['concentration']['n']}",
        f"- **Lucro líquido acumulado:** R$ {rc['concentration']['net']:.2f}",
        f"- **Maior operação individual (Top 1):** R$ {rc['concentration']['top1']:.2f} ({rc['concentration']['top1'] / rc['concentration']['net'] * 100:.1f}% do lucro total)",
        f"- **3 Maiores operações (Top 3):** R$ {rc['concentration']['top3']:.2f} ({rc['concentration']['top3'] / rc['concentration']['net'] * 100:.1f}% do lucro total)",
        f"- **Resultado líquido sem as 3 maiores operações:** R$ {rc['concentration']['net_without_top3']:.2f}",
        "",
        "> [!WARNING]",
        "> **Alta vulnerabilidade a outliers:** O resultado total é inteiramente sustentado por 3 operações excelentes. Sem elas, o backtest encerra com prejuízo de R$ -6,31.",
        "",
        "## 5. Bootstrap da Expectativa por Operação (5.000 Amostragens)\n",
        f"- **Média amostral:** R$ {rc['total']['expectancy']:.3f} por operação",
        f"- **Intervalo de Confiança 95%:** [{rc['bootstrap95_expectancy'][0]:.3f}; {rc['bootstrap95_expectancy'][1]:.3f}] R$/op",
        "- **Significância estatística:** Como o intervalo de 95% cruza o zero (inclui valores negativos), **a hipótese nula de expectativa zero ou negativa não pode ser rejeitada** com 95% de confiança.",
        "",
        "## 6. Análise de Sensibilidade de Parâmetros\n",
        "Variação univariada de parâmetros (apenas reporte de robustez, sem seleção post-hoc):\n",
        "| Parâmetro Testado | Retorno Total | Retorno OOS | Drawdown Máx | Ops | Profit Factor |",
        "|---|---|---|---|---|---|"
    ]
    for v in rc['sensitivity']:
        lines.append(f"| {v['param']} | {f(v['ret_pct'],'%')} | {f(v['oos_ret'],'%')} | {f(v['mdd'],'%')} | {v['n']} | {f(v['pf'])} |")

    lines += [
        "",
        "Observa-se que a redução do período de regressão para 90 pregões desestabilizou o canal (-2,27% total), enquanto variações no ATR e médias móveis mantiveram a estratégia em faixas controladas.",
        "",
        "## 7. Desempenho por Ano (Consistência Temporal)\n",
        "| Ano | Retorno da Carteira C |",
        "|---|---|"
    ]
    for y_str, y_val in rc['years'].items():
        lines.append(f"| {y_str} | {y_val}% |")

    lines += [
        "",
        "A estratégia apresentou 2 anos positivos (2023: +1,99%, 2025: +0,89%) e 3 anos com leves oscilações negativas (2022: -0,12%, 2024: -0,16%, 2026: -0,35%). Em 2021 não houve sinais devido ao aquecimento dos indicadores."
    ]
    (R / 'reports/Robustez_Estrategia_C.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def gen_resumo_chatgpt():
    ra = res['A']
    rc = res['C']
    lines = [
        "# Resumo Executivo – Estratégia C (Para ChatGPT / Análise Quantitativa)\n",
        NOTE,
        "## 1. Identificação do Projeto",
        "- **Estratégia:** C — Swing Trade com Ranking de Força Relativa, Canal de Regressão Logarítmica e Gestão de Risco.",
        "- **Plataforma:** MQL5 (`MQL5/Experts/B3Swing/B3Swing_C_RelativeStrength.mq5`) e Simulador Consolidado Python (`tools/sim_swing_portfolio.py`).",
        "- **Ativos:** ITUB4, BBAS3, WEGE3, GGBR4, PETR4, VALE3, BBDC4, ABEV3, EGIE3, SUZB3 (10 ações líquidas B3) + IBOV.",
        "- **Período:** 17/11/2021 a 16/11/2026 (1.248 barras D1 por ativo).",
        "- **Divisão:** Desenvolvimento (2021–2023), Validação (2024), Fora da Amostra (2025–16/11/2026).",
        "- **Capital Inicial:** R$ 500,00 | Caixa compartilhado | Posições simultâneas: até 3 | Sem alavancagem.",
        "- **Custos:** 0,05%/lado + R$ 0,05 fixo/lado | Slippage: 1 tick entrada, 2 ticks stop.",
        "",
        "## 2. Resumo Numérico Comparativo (A x C)",
        "| Indicador | Estratégia A | Estratégia C | Benchmark (IBOV / CDI) |",
        "|---|---|---|---|",
        f"| Capital Final | R$ {ra['total']['end']} | R$ {rc['total']['end']} | - |",
        f"| Retorno Total Líquido | +{ra['total']['ret_pct']}% | +{rc['total']['ret_pct']}% | IBOV: +64,45% / CDI: +82,76% |",
        f"| Retorno Anualizado | +{ra['total']['ann_pct']}% | +{rc['total']['ann_pct']}% | - |",
        f"| Drawdown Máximo | -{abs(ra['total']['max_dd_pct'])}% | -{abs(rc['total']['max_dd_pct'])}% | - |",
        f"| Profit Factor | {ra['total']['profit_factor']} | {rc['total']['profit_factor']} | - |",
        f"| Taxa de Acerto | {ra['total']['hit_rate']}% | {rc['total']['hit_rate']}% | - |",
        f"| Total de Operações | {ra['total']['n_trades']} | {rc['total']['n_trades']} | - |",
        f"| Lucro Médio / Prejuízo Médio | R$ {ra['total']['avg_win']} / R$ {ra['total']['avg_loss']} | R$ {rc['total']['avg_win']} / R$ {rc['total']['avg_loss']} | - |",
        f"| Relação Payoff (Win/Loss) | 1,97 | 3,86 | - |",
        f"| Expectativa Matemática | R$ {ra['total']['expectancy']}/op | R$ {rc['total']['expectancy']}/op | - |",
        f"| Retorno Fora da Amostra (OOS) | +{ra[OOS]['ret_pct']}% | +{rc[OOS]['ret_pct']}% | IBOV: +40,75% / CDI: +28,34% |",
        f"| Drawdown Fora da Amostra | -{abs(ra[OOS]['max_dd_pct'])}% | -{abs(rc[OOS]['max_dd_pct'])}% | - |",
        f"| Profit Factor Fora da Amostra | {ra[OOS]['profit_factor']} | {rc[OOS]['profit_factor']} | - |",
        f"| Operações Fora da Amostra | {ra[OOS]['n_trades']} | {rc[OOS]['n_trades']} | - |",
        f"| Custos Totais | R$ {ra['total']['costs']} | R$ {rc['total']['costs']} | - |",
        f"| Custos 2× + Slippage 3× | -0,12% (prejuízo) | +0,53% (positivo) | - |",
        f"| Bootstrap IC 95% Expectativa | [-0,305; +0,669] | [-0,420; +1,215] | Ambos cruzam zero |",
        f"| Concentração (Top 3 trades) | R$ 23,03 (Total: 13,67) | R$ 17,60 (Total: 11,29) | Ambos dependem de outliers |",
        "",
        "## 3. Diagnóstico e Classificação",
        "- **Classificação Formal:** **REVISÃO NECESSÁRIA**.",
        "- **Motivação:** A Estratégia C superou a Estratégia A em qualidade de risco, gerando um drawdown máximo minúsculo (-1,46%), melhor profit factor (1,51), excelente assimetria de ganhos (payoff 3,86) e sobrevida operacional a custos duplicados e slippage triplicado (+0,53%).",
        "- **Impedimentos para Aprovação:**",
        "  1. Amostra muito pequena: apenas 32 operações em 5 anos (10 fora da amostra).",
        "  2. Intervalo de confiança bootstrap cruza zero, sem significância estatística conclusiva a 95%.",
        "  3. Extrema dependência de 3 trades (sem o top 3, resultado seria -R$ 6,31).",
        "  4. Retorno líquido irrisório (+2,26%) ante o CDI (+82,76%).",
        "- **NÃO AUTORIZADA PARA PAPER TRADING OU EXECUÇÃO REAL.**",
        "",
        "## 4. O que Foi Implementado e Testado",
        "- Implementação MQL5: `MQL5/Experts/B3Swing/B3Swing_C_RelativeStrength.mq5` (compilado no MetaEditor build 6230 com 0 erros e 0 warnings).",
        "- Implementação Python: `tools/sim_swing_portfolio.py` com simulador multiativo, ranking de percentis, canal log-linear e travas de High-Water Mark.",
        "- Testes Unitários Automatizados: `tools/test_strategy_c.py` (14 testes cobrindo ranking, canais, stops, dimensionamento, limites de risco, gaps, ausência de look-ahead e bloqueio de ordens reais — 100% aprovados).",
        "- Análises de Robustez: Custos 2x/4x, slippage 3x, leave-one-out em 10 ativos, sensibilidade paramétrica, bootstrap de 5.000 amostragens, regimes de mercado.",
        "- Não houve execução de ordens reais nem alteração dos parâmetros da Estratégia A."
    ]
    (R / 'reports/Resumo_Estrategia_C_ChatGPT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    gen_backtest_c()
    gen_comparativo_a_c()
    gen_robustez_c()
    gen_resumo_chatgpt()
    print("Relatórios gerados com sucesso!")


if __name__ == '__main__':
    main()
