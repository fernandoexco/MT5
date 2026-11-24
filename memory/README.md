# Arquitetura de Memória e Aprendizado Multi-IA

Este diretório contém a **memória compartilhada e persistente do projeto MCP_MT5**, estruturada para ser lida e atualizada de forma unificada por **qualquer Inteligência Artificial**:

- **OpenAI:** ChatGPT, GPT-4o, Codex, Custom Assistants
- **Anthropic:** Claude Code, Claude 3.5 Sonnet, Claude Opus
- **Google:** Gemini 1.5/2.0, Antigravity
- **xAI:** Grok
- **Ferramentas de Desenvolvimento:** GitHub Copilot, Cursor, OpenCode, Aider, Windsurf

---

## Estrutura dos Arquivos

1. **[`bastao.md`](./bastao.md)**:
   - **O que é:** Passagem de bastão entre sessões.
   - **Conteúdo:** Estado atual do projeto, entregas recentes, validações, pendências críticas, limites operacionais e frase recomendada de retomada.
   - **Regra de atualização:** Sobrescrito ao final de cada sessão via `/registrar`.
   - *Nota de compatibilidade:* Também espelhado em `.codex/memory/bastao-codex.md` para clientes legados.

2. **[`aprendizados.md`](./aprendizados.md)**:
   - **O que é:** Diário consolidado de lições aprendidas, decisões arquiteturais e armadilhas técnicas (*gotchas*).
   - **Conteúdo:** Seções cronológicas e temáticas no padrão:
     `[Contexto/Sintoma] -> [Causa Confirmada] -> [Correção Efetuada] -> [Regra de Prevenção] -> [Evidência/Arquivo]`.
   - **Regra de atualização:** Nunca sobrescrever; novos aprendizados são anexados na data da sessão.

---

## Como Qualquer IA Deve Interagir com a Memória

### Ao Iniciar a Sessão:
1. Ler [`bastao.md`](./bastao.md) para absorver o estado mais recente e as restrições inegociáveis.
2. Consultar seções relevantes de [`aprendizados.md`](./aprendizados.md) antes de propor mudanças de arquitetura ou tentar soluções já descartadas.
3. Consultar as skills disponíveis em `.agents/skills/` ou `.claude/skills/`.

### Ao Finalizar a Sessão:
1. Executar o fluxo da skill `registrar` (disponível em `.agents/skills/registrar/SKILL.md` ou `.claude/skills/registrar/SKILL.md`).
2. Anexar as lições e correções em [`aprendizados.md`](./aprendizados.md).
3. Atualizar o estado em [`bastao.md`](./bastao.md).
