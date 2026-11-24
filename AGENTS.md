# Memória e Instruções Globais para Agentes de IA

Este arquivo define as diretrizes universais de operação para **qualquer agente de Inteligência Artificial** (GPT/Codex, Claude, Grok, OpenCode, Antigravity, Gemini, GitHub Copilot, Cursor, etc.) atuando no repositório **MCP_MT5**.

---

## 1. Memória do Projeto e Passagem de Bastão

Ao iniciar qualquer interação neste projeto:
1. **Leia [`memory/bastao.md`](file:///Y:/Claude/MCP_MT5/memory/bastao.md)** (ou `.codex/memory/bastao-codex.md`) para assimilar o estado mais recente das entregas, validações quantitativas, sinais em aberto e pendências.
2. **Consulte [`memory/aprendizados.md`](file:///Y:/Claude/MCP_MT5/memory/aprendizados.md)** (ou `.codex/memory/aprendizados.md`) para conhecer decisões arquiteturais já validadas, falhas corrigidas e armadilhas técnicas (*gotchas*). Nunca reutilize conclusões históricas sem verificar as evidências e o código fonte.
3. **Ao finalizar a tarefa:** Execute a skill `/registrar` para registrar novos aprendizados em `memory/aprendizados.md` e atualizar `memory/bastao.md`.

---

## 2. Ecossistema de Skills Disponíveis

O repositório padroniza procedimentos operacionais em formato aberto (Agent Skills Specification: YAML frontmatter + Markdown). As skills estão sincronizadas em `.agents/skills/`, `.claude/skills/` e `skills/`:

1. **`registrar`**: Automatiza a extração e o registro de aprendizados, armadilhas técnicas e passagem de bastão multi-IA.
2. **`mql5-b3-quant-tester`**: Desenvolvimento, compilação CLI (`MetaEditor64.exe`), validação de EAs MQL5, simulador Python multiativo e bateria estatística de robustez (bootstrap, estresse de custos, leave-one-out).
3. **`b3-swing-ifr2-alta-eficiencia`**: Estratégia quantitativa principal (+40,36% a.a., PF 4,95, Hit Rate 82,05%, DD -3,68%). Reversão à média em IFR(2) < 25, filtro SMA(20), força relativa $RS_{60} > 0$ e dimensionamento Half-Kelly com caixa remunerado a 100% do CDI.
4. **`b3-swing-ponto-continuo`**: Setup seguidor de tendência (+156,84% em 5 anos, PF 1,33, DD -15,93%). Recuos até a MME 21, confirmação de rompimento de máxima e alvo assimétrico de 2× ATR.
5. **`organizar-acervo-bibliografico`**: Organização de acervos de livros, PDFs e apostilas (pasta plana, nomenclatura padronizada e OCR paralelo Tesseract).

---

## 3. Conexão Automática ao MetaTrader 5 (MCP)

**Conexão validada em 23/11/2026 e 24/11/2026.** O terminal Clear Investimentos MT5 (build 6230) conecta-se via servidor local MCP na porta `127.0.0.1:22346` sob a conta da Clear.

- Na primeira tarefa que exigir acesso ao MT5 em cada sessão, utilize o endpoint MCP `terminal`. Se o terminal estiver fechado, abra `C:/Program Files/Clear Investimentos MT5 Terminal/terminal64.exe` e aguarde a resposta do servidor local.
- Se o MCP direto não estiver ativo na sessão da IA, utilize o cliente MCP `tools/mt5mcp.py`, que lê a configuração local em `.mcp.json`.
- **Segurança de Credenciais:** Nunca exponha senhas, tokens ou dados de conta no chat, em relatórios ou em commits do Git.
- Confirme a conexão com a ferramenta `get_trading_account_info` e valide se a conta retornada pertence ao servidor `ClearInvestimentos-CLEAR`.

---

## 4. Regras Operacionais e Limites de Segurança

- **PROIBIDO ENVIO DE ORDENS REAIS SEM AUTORIZAÇÃO:** O modo padrão do projeto é exclusivamente de simulação, backtest e paper trading. Qualquer envio real à bolsa exige prévia apresentação detalhada e aprovação explícita do usuário.
- **Limitação de Lote Fracionário:** O servidor MT5 da Clear não possui símbolos fracionários (sem sufixo `F`). Para capitais pequenos (R$ 500), simulações de carteira multiativo com frações de lote ou ações unitárias devem ser executadas no simulador consolidado em Python sobre candles D1 reais.
- **Integridade Científica:** Nunca invente resultados de backtest, nunca ignore custos/slippages e nunca otimize parâmetros usando dados do período fora da amostra (*out-of-sample*).
