---
name: registrar
description: Registra aprendizados, correções do usuário, falhas, armadilhas técnicas e decisões de uma sessão nas skills e na memória do projeto para qualquer IA (GPT, Claude, Grok, OpenCode, Antigravity, Gemini, GitHub Copilot, Cursor). Use quando o usuário pedir "/registrar", "registra os aprendizados", "guardar as lições", "salvar aprendizados", "passagem de bastão" ou "atualizar a memória".
---

# Registrar Aprendizados da Sessão (Universal Multi-IA)

Transforma o trabalho da sessão em conhecimento durável, conciso e verificável para **qualquer agente de Inteligência Artificial** (GPT/Codex, Claude, Grok, OpenCode, Antigravity, Gemini, GitHub Copilot, Cursor, etc.), evitando que futuras sessões repitam erros, redescubram armadilhas ou desfaçam decisões já validadas.

---

## 1. Revisar e Extrair da Conversa Atual
Antes de registrar, revise os comandos executados, logs, commits e saídas reais de ferramentas na sessão:
- **Procedimentos que funcionaram:** fluxos reproduzíveis com sucesso comprovado (ex.: comandos CLI, consultas MCP, scripts de backtest).
- **Correções do usuário:** mudanças solicitadas explicitamente e o motivo subjacente.
- **Erros técnicos e de compilação:** mensagens exatas de erro, incompatibilidades de sintaxe, tipos ou bibliotecas.
- **Armadilhas técnicas (pegadinhas):** comportamentos contraintuitivos do ambiente, corretora, MT5, dados ou APIs.
- **Decisões metodológicas:** critérios estatísticos, períodos, universos e premissas financeiras adotadas.
- **Falsos positivos / Tentativas descartadas:** caminhos que pareciam promissores mas falharam nos testes.

> **Regra de Ouro da Integridade:** Diferencie fatos verificados (código testado, saída real de terminal) de estimativas ou hipóteses não comprovadas. Nunca invente causas ou resultados.

---

## 2. Arquitetura Universal de Destinos de Memória

Para garantir que **qualquer IA** acesse e atualize a mesma base de conhecimento, mantenha os seguintes arquivos sincronizados:

| Tipo de Informação | Destino Canônico | Destinos Espelho / Compatibilidade |
|---|---|---|
| **Histórico e aprendizados do projeto** (lições, armadilhas, vieses) | `memory/aprendizados.md` | `.codex/memory/aprendizados.md` |
| **Passagem de bastão e estado atual** (entregas, pendências, próximo passo) | `memory/bastao.md` | `.codex/memory/bastao-codex.md` |
| **Skills operacionais reutilizáveis** (procedimentos em Markdown + YAML) | `.agents/skills/<nome>/SKILL.md` (Universal) | `.claude/skills/<nome>/SKILL.md`<br>`skills/<nome>/SKILL.md` |
| **Instruções de entrada por IA** (pontos de descoberta automáticos) | `AGENTS.md` (Geral / OpenAI / Grok / OpenCode)<br>`CLAUDE.md` (Anthropic Claude Code)<br>`GEMINI.md` (Google Gemini / Antigravity)<br>`.github/copilot-instructions.md` (Copilot)<br>`.cursorrules` (Cursor) | Devem apontar para `memory/` e `.agents/skills/`. |

---

## 3. Padrão de Registro de Lições e Armadilhas (5 Campos)

Para cada lição, erro ou pegadinha relevante, registre no formato enxuto:
> **[Contexto/Sintoma]** $\to$ **[Causa Confirmada]** $\to$ **[Correção Efetuada]** $\to$ **[Regra de Prevenção]** $\to$ **[Evidência/Arquivo]**

### Exemplo Real do Projeto:
- **Sintoma:** MetaEditor retorna `error 294: arrays are passed by reference only`.
- **Causa:** No MQL5, parâmetros do tipo array não podem ser passados por valor (`string arr[]`).
- **Correção:** Adicionar o operador de referência `&` na assinatura (`string &arr[]`).
- **Prevenção:** Sempre passar arrays por referência em funções MQL5.
- **Evidência:** [`B3Swing_C_RelativeStrength.mq5`](file:///Y:/Claude/MCP_MT5/MQL5/Experts/B3Swing/B3Swing_C_RelativeStrength.mq5).

---

## 4. Criação e Atualização de Skills Multi-IA

Se a sessão desenvolveu um fluxo novo que se repetirá em outros projetos ou tarefas:
1. Crie o arquivo `SKILL.md` contendo frontmatter YAML padronizado:
   ```yaml
   ---
   name: nome-da-skill
   description: Descrição clara das capacidades e lista de gatilhos acionáveis por qualquer IA.
   ---
   ```
2. Escreva instruções imperativas e acionáveis, independentes de um modelo específico de IA.
3. Salve e replique a pasta da skill nos diretórios de descoberta:
   - `.agents/skills/<nome>/` (Universal: Antigravity, Codex, Gemini, OpenCode)
   - `.claude/skills/<nome>/` (Claude Code)
   - `skills/<nome>/` (Raiz acessível globalmente)

---

## 5. Procedimento de Fechamento (`/registrar`)

Ao ser acionada em qualquer IA, a ferramenta deve:
1. **Atualizar `memory/aprendizados.md`** (e seu espelho `.codex/memory/aprendizados.md`) com a nova seção da data atual.
2. **Atualizar `memory/bastao.md`** (e seu espelho `.codex/memory/bastao-codex.md`) sobrescrevendo o resumo de estado, entregas, pendências reais e frase de retomada.
3. **Sincronizar skills novas ou modificadas** entre `.agents/skills/`, `.claude/skills/` e `skills/`.
4. **Exibir resumo ao usuário:**
   - Tabela: `Arquivo modificado/criado | O que foi registrado`.
   - Principais pegadinhas e aprendizados documentados.
   - Pendências reais que exigem validação ou autorização.
   - Frase acionável recomendada para iniciar a próxima sessão em qualquer IA.
