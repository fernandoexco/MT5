# Instruções do Projeto — Claude Code

Diretrizes específicas e comandos de referência para o assistente **Claude Code** no projeto **MCP_MT5**.

---

## 1. Memória do Projeto e Passagem de Bastão

- **Início de Sessão:** Leia obrigatoriamente [`memory/bastao.md`](file:///Y:/Claude/MCP_MT5/memory/bastao.md) e consulte [`memory/aprendizados.md`](file:///Y:/Claude/MCP_MT5/memory/aprendizados.md) antes de planejar intervenções ou executar testes.
- **Fim de Sessão (`/registrar`):** Quando o usuário solicitar `/registrar` ou encerramento, execute a skill em [`.claude/skills/registrar/SKILL.md`](file:///Y:/Claude/MCP_MT5/.claude/skills/registrar/SKILL.md), gravando os aprendizados em `memory/aprendizados.md` e atualizando o estado do projeto em `memory/bastao.md`.

---

## 2. Skills Nativas

Claude Code localiza skills automaticamente em `.claude/skills/`:
- `b3-swing-ifr2-alta-eficiencia`
- `b3-swing-ponto-continuo`
- `mql5-b3-quant-tester`
- `organizar-acervo-bibliografico`
- `registrar`

---

## 3. Comandos Úteis

- **Compilar EA MQL5 (Headless MetaEditor):**
  ```powershell
  & "C:\Program Files\Clear Investimentos MT5 Terminal\MetaEditor64.exe" /compile:"Y:\Claude\MCP_MT5\MQL5\Experts\B3Swing\B3Swing_C_RelativeStrength.mq5" /log:"compile.log"
  Get-Content "compile.log"
  ```
- **Executar Testes Unitários:**
  ```powershell
  python tools/test_strategy_c.py
  python tools/test_swing.py
  python tools/test_backtest.py
  ```
- **Rastrear Sinais IFR2 ao Vivo via MCP MT5:**
  ```powershell
  python tools/agente_operador_ifr2.py --scan
  ```

---

## 4. Regras Críticas de Segurança

1. **Ordens Reais Proibidas:** Nunca envie ordens reais nem ative negociação automática real sem consentimento explícito.
2. **Credenciais Protegidas:** Nunca exponha o token `.mcp.json` ou credenciais da corretora em arquivos rastreados pelo Git.
