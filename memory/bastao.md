# Passagem de Bastão — Memória Unificada Multi-IA

Atualizado em 24/11/2026, America/Sao_Paulo.
Compatível com: **GPT / Codex, Claude, Grok, OpenCode, Antigravity, Gemini, GitHub Copilot, Cursor e qualquer agente autônomo**.

---

## 1. Entregas Recentes e Estado do Projeto

- **Conexão MT5 ao Vivo via MCP Operacional:**
  - Endpoint local JSON-RPC em `127.0.0.1:22346` autenticado no servidor `ClearInvestimentos-CLEAR` (MetaTrader 5 build 6230).
  - 67 ferramentas operacionais MCP ativas (`get_chart_history`, `get_trading_account_info`, `get_time_information`, etc.).
  - Base de dados D1 sincronizada até o pregão de 23/11/2026 para todo o universo (PETR4, VALE3, ITUB4, BBDC4, BBAS3, WEGE3, GGBR4, ABEV3, EGIE3, SUZB3, BOVA11 e IBOV).

- **Estratégia IFR2 de Alta Eficiência (Setup Principal Aprovado):**
  - Retorno em 1 ano recente (24/11/2025 a 23/11/2026): **+40,36% líquido** (R$ 500 &rarr; R$ 701,78).
  - **Profit Factor:** **4,95** | **Taxa de Acerto:** **82,05%** (32 acertos / 7 perdas).
  - **Drawdown Máximo:** Apenas **-3,68%**.
  - **Significância Estatística:** Intervalo Bootstrap 95% de **[+R$ 1,912 ; +R$ 5,326]** por trade (hipótese nula de vantagem zero rejeitada com folga).
  - **Sinal Ativo em Aberto (24/11/2026):** Sinal de compra em **WEGE3** no fechamento de 23/11/2026 ($Close = \text{R\$} 49,91 > SMA(20) = \text{R\$} 49,21$, $IFR(2) = 10,4 < 25$, $RS_{60} = +6,27\%$). Lote calculado para R$ 500: 4 ações inteiras.
  - Relatórios e painel: [`reports/RELATORIO_SWING_IFR2.md`](file:///Y:/Claude/MCP_MT5/reports/RELATORIO_SWING_IFR2.md) e [`reports/dashboard_swing_ifr2.html`](file:///Y:/Claude/MCP_MT5/reports/dashboard_swing_ifr2.html).

- **Estratégia Ponto Contínuo (PC - Seguidora de Tendência):**
  - Recuos na MME 21 em tendência primária de alta com $RS_{60} > 0$ e alvo assimétrico de 2× ATR.
  - Resultado em 5 anos: **+156,84% líquido** (R$ 500 &rarr; R$ 1.284,22), PF **1,33**, acerto **52,33%**, DD máx **-15,93%**.
  - Documentação em [`reports/RELATORIO_ESTRATEGIAS_ACERVO.md`](file:///Y:/Claude/MCP_MT5/reports/RELATORIO_ESTRATEGIAS_ACERVO.md).

- **Estratégia C (Força Relativa e Canal de Alta):**
  - Código MQL5: [`B3Swing_C_RelativeStrength.mq5`](file:///Y:/Claude/MCP_MT5/MQL5/Experts/B3Swing/B3Swing_C_RelativeStrength.mq5), compilado com 0 erros/avisos.
  - Resultado: +2,26% em 5 anos, DD -1,46%, PF 1,51. Classificação: **REVISÃO NECESSÁRIA** (amostra pequena de 32 trades e dependência de outliers).

- **Acervo Bibliográfico Digital e Extração de Texto:**
  - Padrão da Biblioteca Particular integrado: pasta plana, nomenclatura bibliográfica padronizada e OCR paralelo com Tesseract.
  - Scripts operacionais: [`inspecionar_acervo.py`](file:///Y:/Claude/MCP_MT5/skills/organizar-acervo-bibliografico/scripts/inspecionar_acervo.py) e [`extrair_ocr_acervo.py`](file:///Y:/Claude/MCP_MT5/skills/organizar-acervo-bibliografico/scripts/extrair_ocr_acervo.py).

- **Ecossistema de Skills Multi-IA Padronizado:**
  - Todas as 5 skills sincronizadas em `.agents/skills/`, `.claude/skills/` e `skills/`:
    1. `b3-swing-ifr2-alta-eficiencia`
    2. `b3-swing-ponto-continuo`
    3. `mql5-b3-quant-tester`
    4. `organizar-acervo-bibliografico`
    5. `registrar`

---

## 2. Validação, Regras e Limites de Segurança

1. **Bloqueio Inegociável de Ordens Reais:**
   - Modo padrão é **estritamente simulação e paper trading**.
   - Qualquer envio de ordens reais à corretora exige apresentação prévia de parâmetros, conta de destino e autorização explícita do usuário.
   - Os Expert Advisors em MQL5 possuem bloqueio programático via `MQLInfoInteger(MQL_TESTER)`.

2. **Infraestrutura Clear MT5:**
   - O servidor `ClearInvestimentos-CLEAR` não disponibiliza contratos fracionários (sem símbolos `F`). O lote mínimo na corretora é 100 ações.
   - O Strategy Tester do MT5 recusa ordens em contas pequenas devido ao lote mínimo. Portanto, as simulações multiativo com ações inteiras e caixa compartilhado utilizam o motor Python sobre dados reais do MT5.

3. **Remuneração de Caixa a 100% do CDI:**
   - O caixa livre desinvestido é corrigido diariamente pela taxa do CDI (SGS 12 do Banco Central), simulando operações compromissadas automáticas da B3.

---

## 3. Próximos Passos e Pendências

1. **Execução Supervisionada do Sinal WEGE3:**
   - Sinal ativo gerado em 23/11/2026. Apresentar dados operacionais ao usuário antes de qualquer ação.
2. **Ampliação do Universo de Rastreamento:**
   - Avaliar inclusão das BDRs de maior liquidez (NVDC34, MSFT34, AAPL34) ou ativos do índice Small Caps (SMLL) no rastreamento diário do IFR2.
3. **Manutenção da Memória:**
   - Ao final de cada sessão, qualquer IA deve executar o fluxo `/registrar` para registrar novas descobertas em `memory/aprendizados.md` e atualizar este arquivo.

---

## 4. Frase de Retomada para Próxima Sessão

> *"Leia `memory/bastao.md` e `memory/aprendizados.md` para retomar o estado das estratégias, verificar a conexão MCP do MT5 e monitorar os sinais de Swing Trade."*
