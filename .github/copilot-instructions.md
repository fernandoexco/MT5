# GitHub Copilot Instructions — MCP_MT5

Diretrizes de contexto e desenvolvimento para o **GitHub Copilot** no repositório **MCP_MT5**.

---

## 1. Contexto do Repositório

O **MCP_MT5** é um projeto de engenharia quantitativa e automação de swing trade na B3 (ações brasileiras) utilizando MetaTrader 5 (Clear Investimentos), Python e Model Context Protocol (MCP).

- **Estratégias Principais:**
  - `b3-swing-ifr2-alta-eficiencia`: Reversão à média com IFR(2) < 25, filtro SMA(20), Força Relativa de 60 dias ($RS_{60} > 0$ vs IBOV), Half-Kelly e caixa a 100% do CDI (+40,36% a.a., PF 4,95).
  - `b3-swing-ponto-continuo`: Recuos técnicos até a MME 21 em tendência de alta (+156,84% em 5 anos, PF 1,33).
  - `B3Swing_C_RelativeStrength`: Ranking transversal de força relativa com regressão log-linear.

---

## 2. Memória e Regras de Registro

- Sempre consulte [`memory/bastao.md`](../memory/bastao.md) e [`memory/aprendizados.md`](../memory/aprendizados.md) para verificar o estado recente e as armadilhas técnicas conhecidas.
- As skills operacionais do projeto residem em `.agents/skills/`, `.claude/skills/` e `skills/`.
- Quando o usuário solicitar registrar lições ou atualizar a memória, siga o padrão de 5 campos documentado em `skills/registrar/SKILL.md`.

---

## 3. Padrões de Código e Pegadinhas Técnicas

- **MQL5:**
  - Parâmetros de array em funções **devem ser passados por referência** (`string &arr[]`), caso contrário o MetaEditor emite `error 294: arrays are passed by reference only`.
  - Todo Expert Advisor deve conter bloqueio de negociação real via `MQLInfoInteger(MQL_TESTER)` para segurança.
- **Python:**
  - Nunca utilize funções com look-ahead bias em simulações quantitativas.
  - Sinais são gerados com dados fechados em $D-1$ e preenchidos na abertura de $D0$.
  - Trate divisões com denominador dinâmico (ex.: percentis transversais com `n <= 1`).
- **Segurança:** Nunca comite `.mcp.json` ou credenciais da corretora.
