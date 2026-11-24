# Instruções do Projeto — Gemini & Antigravity

Diretrizes para os agentes **Google Gemini Code Assist** e **Antigravity** no projeto **MCP_MT5**.

---

## 1. Memória Unificada

- **Inicialização:** Consulte [`memory/bastao.md`](file:///Y:/Claude/MCP_MT5/memory/bastao.md) para verificar o estado operacional atual e [`memory/aprendizados.md`](file:///Y:/Claude/MCP_MT5/memory/aprendizados.md) para consultar armadilhas técnicas e decisões metodológicas prévias.
- **Encerramento:** Ao pedido de `/registrar` ou finalização de tarefa, atualize a base de conhecimento executando o fluxo da skill `registrar` em `.agents/skills/registrar/SKILL.md`.

---

## 2. Skills no Padrão Agent Skills Specification

O Antigravity e o Gemini descobrem as skills localizadas em `.agents/skills/`:
- [`b3-swing-ifr2-alta-eficiencia`](file:///Y:/Claude/MCP_MT5/.agents/skills/b3-swing-ifr2-alta-eficiencia/SKILL.md)
- [`b3-swing-ponto-continuo`](file:///Y:/Claude/MCP_MT5/.agents/skills/b3-swing-ponto-continuo/SKILL.md)
- [`mql5-b3-quant-tester`](file:///Y:/Claude/MCP_MT5/.agents/skills/mql5-b3-quant-tester/SKILL.md)
- [`organizar-acervo-bibliografico`](file:///Y:/Claude/MCP_MT5/.agents/skills/organizar-acervo-bibliografico/SKILL.md)
- [`registrar`](file:///Y:/Claude/MCP_MT5/.agents/skills/registrar/SKILL.md)

---

## 3. Diretrizes de Execução

- **MetaTrader 5 via MCP:** Priorize consultas ao terminal Clear MT5 usando o cliente local `tools/mt5mcp.py` ou a integração MCP ativa.
- **Risco e Segurança:** Modo padrão restrito a simulação/paper trading. Bloqueio nativo de ordens reais em MQL5 com `MQLInfoInteger(MQL_TESTER)`.
