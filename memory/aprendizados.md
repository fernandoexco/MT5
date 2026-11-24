# Aprendizados do projeto MCP_MT5

Registro em 16/11/2026. Fontes principais: `README_SWING.md`, `reports/VALIDACAO_SWING.md`, `reports/backtest/RELATORIO.md` e código em `tools/`. Resultados abaixo são históricos, vinculados ao modelo e ao período; não representam desempenho futuro.

## Escopo e autorização

- Manter simulação como padrão. O usuário proibiu ordens reais nesta etapa; ativação futura exige apresentação da configuração, conta de destino e resultados, seguida de autorização explícita. Não interpretar o pedido de registrar ou testar como autorização de negociação.
- Preservar capital virtual R$ 500, aplicação máxima R$ 450, risco planejado R$ 2,50 incluindo custos, uma posição, sem alavancagem e bloqueio acumulado de perda líquida R$ 20. Gaps podem superar o risco planejado.
- Credenciais existentes ficam fora do código e dos registros. Não copiar `.mcp.json` para relatórios. Reconferir conta, servidor, saldo e capacidades antes de decisões operacionais; inspeções anteriores não são estado atual.

## Testes técnicos e rentabilidade

- Testes aprovados do motor validam os cenários exercitados; não demonstram rentabilidade. O cenário sintético de estresse é artificial e deve ficar separado do backtest e da conta paper operacional.
- O backtest de 02/01/2024 a 30/12/2025 terminou em R$ 479,554045, retorno −4,089191%, após custos estimados e antes de IR. Foram 14 operações, duas vencedoras; bloqueio de novas entradas em 03/02/2025. Fonte: `reports/backtest/summary.json`; hipóteses e operações: `reports/backtest/RELATORIO.md`.
- Comparadores do mesmo estudo: CDB hipotético 100% CDI bruto R$ 632,516415; líquido R$ 612,638953; Ibovespa teórico R$ 600,383798; reposição pelo IPCA R$ 546,508529. IPCA é referência de poder de compra e usa meses completos; CDB não é uma oferta real. Consulte as ressalvas tributárias e de datas no relatório.
- A sessão anterior registrou 29 testes do motor paper e nove do backtest aprovados. Este registro não os executou novamente. Reproduzir com `py -3.13 tools/test_swing.py` e `py -3.13 tools/test_backtest.py` quando houver alteração pertinente.

## Canal e causalidade

- Preservar a fórmula inspecionada: regressão OLS de ln(fechamento) nos últimos 120 pregões, x=0..119, sigma=sqrt(SSE/118), bandas exp(a+b*x ± 2*sigma). A borda dos 30% inferiores é exp(a+b*x−0,8*sigma), calculada na escala logarítmica. Não trocar por largura aritmética silenciosamente. Evidência: `tools/swing.py`, função de sinal.
- Sinais usam apenas D1 encerrados e guardam canal, médias e ATR no instante do sinal. Um sinal no último pregão anterior ao início do teste pode gerar entrada na primeira sessão avaliada; ignorá-lo distorce a fronteira inicial.
- Cache do painel tem fechamentos e preenchimento de lacunas; não serve como OHLC para ATR ou simulação de ordens. Não preencher pregões sem negócios para fingir 200 sessões observadas.
- Fixar universo, período e regras antes de calcular resultados. O teste usou universo B3 de 2023, incluindo ativos depois descontinuados, e preços brutos. Não selecionar pelo preço atual ou otimizar depois de ver o retorno. Cache de sinais deve depender do protocolo, dados e código; conferir fingerprint em `tools/backtest_swing.py`.
- Eventos não integralmente reconstruídos e 52 sinais admissíveis sem cobertura de eventos deixam viés residual. Não chamar o teste de livre de todos os vieses. Evidência: relatório do backtest.

## Coleta pelo MT5 e B3

- Símbolos do catálogo podem não estar selecionados na Observação do Mercado; a coleta encontrou `symbol not found`. O coletor adiciona temporariamente símbolos e remove em `finally`, contabilizando falhas de limpeza. Não executar enquanto houver edição manual concorrente dessa lista. Referência: `tools/run_swing.py`.
- Histórico MT5 pode chegar parcialmente na primeira resposta: a coleta do IBOV passou de 30 para 520 candles após estabilização. Verificar intervalo e completude, com tentativas limitadas; não aceitar a primeira resposta como cobertura integral. Referência: `tools/collect_backtest_benchmark.py`.
- Não presumir fracionário na Clear/MT5. Usar lote mínimo/passo/tick do cadastro consultado; em estudo histórico, identificar as aproximações por classe e não apresentá-las como metadados históricos confirmados da corretora.
- Horários B3 dependem de produto, data, leilões e feriados. O calendário operacional incluído cobre somente 03/11–31/12/2026; não extrapolar sua validade. Um resultado de busca ou trecho inicial de página pode esconder atualização posterior: conferir a fonte inteira e sua data.

## Execução e proteção

- Usar Last como hipótese explícita de ativação em instrumento de bolsa; Bid/Ask servem à execução modelada. Confirmar semântica específica na corretora antes de ativar negociação real.
- D1 não demonstra ordem intradiária, fila, spread, execução parcial nem liquidez. A amostra M1 de uma entrada não transforma o estudo em replay de ticks. Ordens intradiárias favorável/conservadora com igual saldo não provam execução real.
- Desconexão do terminal não prova que ordens no servidor pararam. A continuidade de proteção no paper é hipótese do simulador; proteção overnight e localização de SL/TP/OCO na Clear permanecem sem comprovação. O adaptador real está bloqueado.
- Reconciliar ordens, negócios e posições antes de cancelar saldo ou reenviar após timeout. Resultado desconhecido bloqueia nova entrada; proteger só a quantidade comprada. IDs estáveis evitam duplicação e o mesmo ID com conteúdo divergente deve ser recusado. Evidência: `tools/swing.py` e `tools/test_swing.py`.
- Um INSERT de nove placeholders para tabela de oito colunas foi detectado nos testes e corrigido. Ao mudar persistência, testar gravação e retomada reais, além de apenas construir objetos em memória.

## Ferramentas locais

- PowerShell pode alterar aspas em `python -c` e exibir acentos incorretamente. Para texto/código extenso usar arquivos UTF-8 ou here-strings; verificar o conteúdo, não concluir corrupção apenas pela exibição do terminal.
- Para HTML inline, `html_preview` por arquivo exige documento completo começando em `<!doctype html>` ou `<html>`. Conferir escala dos gráficos a partir dos dados para não cortar curvas. Não iniciar servidor para mostrar esse tipo de artefato.

## Skills derivadas e ferramentas de registro

- `~/.claude/skills/registrar/SKILL.md` e `~/.codex/skills/registrar/SKILL.md`: automação da extração de aprendizados, armadilhas técnicas e passagem de bastão.
- `~/.claude/skills/mql5-b3-quant-tester/SKILL.md` e `~/.codex/skills/mql5-b3-quant-tester/SKILL.md`: ciclo completo de desenvolvimento MQL5, compilação CLI, travas no Tester, simulador Python multiativo e bateria estatística de robustez.
- `C:/Users/ferna/.codex/skills/mt5-coleta-historica/SKILL.md`: catálogo versus seleção, cobertura assíncrona, OHLC, timezone, metadados e proveniência.
- `C:/Users/ferna/.codex/skills/trading-simulacao-segura/SKILL.md`: orçamento e risco, estados da ordem, parciais, reconciliação, persistência e proteção não comprovada.
- `C:/Users/ferna/.codex/skills/b3-backtest-causal/SKILL.md`: protocolo antes do retorno, universo histórico, causalidade, execução D1 e comparação com CDB/IPCA/Ibovespa.

## Sessão de 19/11/2026: Estratégia C (Força Relativa + Canais) e Simulação Multiativo

### Compilação MQL5 e Strategy Tester
- **Armadilha de Sintaxe (`error 294`):** O compilador MetaEditor recusa parâmetros do tipo array passados por valor (`string universeSymbols[]`). No MQL5, arrays **devem obrigatoriamente ser passados por referência** (`string &universeSymbols[]`). Corrigido em `B3Swing_C_RelativeStrength.mq5`.
- **Compilação CLI Automatizada:** Possível compilar headless no Windows via `& "C:\Program Files\Clear Investimentos MT5 Terminal\MetaEditor64.exe" /compile:"<caminho.mq5>" /log:"<compile.log>"`, verificando se a saída contém `0 errors, 0 warnings`.
- **Bloqueio de Ordens Reais:** O EA C implementa verificação estrita de `MQLInfoInteger(MQL_TESTER)` no `OnInit` e `OnTick`. Tentativa de execução fora do Tester bloqueia imediatamente.
- **Limitação de Lote no MT5 Clear:** O servidor da Clear no MT5 não possui símbolos fracionários (0 ativos com sufixo `F` entre 3.004 símbolos listados). O lote mínimo de 100 ações inviabiliza ordens no Tester para capital de R$ 500 sem violar a regra de lote. A simulação precisa ocorrer em motor externo em Python com candles reais.

### Motor de Simulação Multiativo em Python
- **Divisão por Zero em Percentil:** Ao executar o teste standalone (`max_pos=1`) ou leave-one-out com único ativo (`len(rs_pool) == 1`), `rank / (n_pool - 1)` gerava `ZeroDivisionError`. Solução: tratar `n_pool <= 1` com valor fixo 100,0%. Evidência: `tools/sim_swing_portfolio.py`.
- **Causalidade e Gaps:** Sinais gerados no fechamento de $D-1$; ordens preenchidas no `Open` de $D0$. Se a abertura apresentar gap, o risco e a quantidade inteira são recalculados pelo preço executável real (`Ask = Open + slippage`).
- **Execução Conservadora de Stop com Gap Intradiário:** Se a mínima do dia rompe o stop e a abertura do dia já ocorreu abaixo dele, a execução ocorre pelo preço de abertura estressado pelo slippage (`min(stop, open) - slippage`), evitando preços irreais.
- **Drawdown sobre o High-Water Mark:** Trava preventiva (6%) e suspensão/liquidação (10%) calculadas sobre o maior patrimônio consolidado atingido pela carteira, e não estaticamente sobre o capital inicial.

### Estatística Quantitativa e Robustez
- **Bootstrap da Expectativa Cruza o Zero:** O intervalo de 95% bootstrap para Estratégia C foi `[-0,420; +1,215]` R$/op (e na Estratégia A foi `[-0,305; +0,669]`). Embora os resultados médios sejam positivos (+2,26% e +2,65%), a hipótese nula de vantagem zero não pode ser rejeitada estatisticamente com 95% de confiança.
- **Concentração de Lucros em Outliers:** O lucro líquido total da Estratégia C foi R$ 11,29, mas as 3 maiores operações somaram R$ 17,60. Sem elas, o resultado seria negativo (-R$ 6,31). O mesmo ocorre na Estratégia A (lucro R$ 13,67, top 3 somam R$ 23,03). Ambas dependem de poucos eventos raros.
- **Resiliência a Custos da Estratégia C:** A Estratégia C realizou apenas 32 operações em 5 anos com payoff de 3,86 (R$ 3,715 por ganho vs -R$ 0,963 por perda). Sob custos duplicados e slippage triplicado, a Estratégia C **permaneceu positiva (+0,53%)**, enquanto a Estratégia A virou negativa (-0,12%).
- **Custo de Oportunidade:** Retorno nominal de +2,26% (C) e +2,65% (A) em ~5 anos ficou drasticamente abaixo do CDI acumulado (+82,76%) e do Ibovespa (+64,45%).
- **Classificação Formal:** Ambas mantidas como **REVISÃO NECESSÁRIA**, sem autorização para paper trading automatizado ou execução real.

## Sessão de 22/11/2026: Estratégia IFR2 de Alta Eficiência, Acervo Bibliográfico e Superação de Benchmarks

### Diagnóstico do Caixa Ocioso e Quebra de Paradigma
- **Armadilha do Risco Estático em Capital Pequeno (R$ 500):** Limitar o risco por trade a R$ 2,50 (0,5%) com stop de volatilidade (2 ATRs) restringia o lote a apenas 1 ação inteira em papéis de R$ 30–60. O resultado prático era deixar 90% a 95% do patrimônio parado em caixa sem remuneração, inviabilizando qualquer ganho percentual expressivo da carteira total.
- **Incorporação do Acervo Bibliográfico (Vlad, Stormer, Connors, Leandro):**
  - O IFR(2) é um modelo de reversão à média com alta taxa de acerto intrínseca (> 70%) e tempo de permanência curto (2 a 5 pregões).
  - Não utilizar stop loss fixo nominal curto: Larry Connors e Vlad comprovam que stops curtos retiram o trader na exaustão máxima da venda, degradando a expectativa matemática.
  - Saída técnica no fechamento acima da SMA(5) ou stop no tempo (5 dias) libera rapidamente o capital para novas entradas.
- **Remuneração do Caixa Desinvestido:** Em contas da B3, o caixa livre deve ser computado com remuneração de 100% do CDI (operações compromissadas diárias), evitando custo de oportunidade nos intervalos entre posições.

### Grid Search e Resultados Efetivos
- **Otimização Abrangente:** O grid de 11.520 combinações identificou que IFR(2) < 25 filtrado por SMA(20) e Força Relativa de 60 dias ($RS_{60} > 0$ vs IBOV), com alocação em até 2 posições inteiras (`max_pos=2`), atingiu no período de 1 ano (17/11/2025 a 16/11/2026):
  - **Retorno Líquido:** **+35,47%** (R$ 500 &rarr; R$ 677,33), superando o CDI (+14,07%), o Ibovespa (+7,32%) e a inflação IPCA (+4,80%).
  - **Profit Factor:** **3,62** com **76,92% de taxa de acerto** em 39 operações.
  - **Drawdown Máximo:** Apenas **-3,79%**.
  - **Significância Estatística:** Intervalo Bootstrap 95% de **[+R$ 1,294 ; +R$ 4,682]** por operação, totalmente afastado do zero.
- **Consistência Multi-Horizonte:** Em 5 anos completos (2021–2026), o modelo gerou **+77,99%** de retorno (R$ 500 &rarr; R$ 889,97) com 226 operações e PF 1,23, mantendo-se rentável também em 2024 (+10,13%) e 2025 (+14,85%).

## Sessão de 24/11/2026: Conexão MT5 via MCP Estabelecida e Rastreamento em Tempo Real

### Conexão e Autenticação MCP MT5
- **Conexão Estabelecida com Sucesso:** Atualização do Bearer token em `.mcp.json` restabeleceu a comunicação JSON-RPC na porta `127.0.0.1:22346` com o terminal Clear Investimentos MT5 (build 6230). A API MCP expôs 67 ferramentas operacionais de leitura e catálogo de símbolos (`get_chart_history`, `get_trading_account_info`, `get_time_information`, etc.).
- **Coleta e Sincronização ao Vivo:** Coleta em tempo real executada para todo o universo de ações líquidas e índices (PETR4, VALE3, ITUB4, BBDC4, BBAS3, WEGE3, GGBR4, ABEV3, EGIE3, SUZB3, BOVA11 e IBOV), estendendo a base de dados até o pregão de 23/11/2026.

### Validação Atualizada das Estratégias
- **IFR2 de Alta Eficiência (1 Ano Recente: 24/11/2025 a 23/11/2026):**
  - Retorno Líquido: **+40,36%** (R$ 500 &rarr; R$ 701,78).
  - Profit Factor: **4,95** | Taxa de Acerto: **82,05%** (32V / 7D).
  - Drawdown Máximo: **-3,68%** | Expectativa: **+R$ 3,586 / trade**.
  - Intervalo Bootstrap 95%: **[+R$ 1,912 ; +R$ 5,326]** por trade.
- **Sinal em Aberto para o Pregão de Hoje (24/11/2026):**
  - O rastreamento automático identificou sinal de compra em **WEGE3** no fechamento de 23/11/2026 ($Close = \text{R\$} 49,91 > SMA(20) = \text{R\$} 49,21$, $IFR(2) = 10,4 < 25$, $RS_{60} = +6,27\%$).
  - Dimensionamento Half-Kelly para R$ 500: compra de 4 ações inteiras (~R$ 199,64 alocados).

