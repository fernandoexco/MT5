---
name: registrar
description: Registra aprendizados, correções do usuário, falhas, armadilhas técnicas e decisões de uma sessão nas skills e na memória do projeto (.codex/memory/). Use quando o usuário pedir "/registrar", "registra os aprendizados", "guardar as lições", "salvar aprendizados" ou atualizar a passagem de bastão.
---

# Registrar Aprendizados da Sessão

Transforma o trabalho da sessão em conhecimento durável, conciso e verificável, evitando que sessões futuras repitam erros, redescubram armadilhas ou desfaçam decisões já tomadas.

## 1. Revisar e Extrair
Antes de escrever, revise os comandos executados, logs, commits e saídas reais de ferramentas na sessão:
- **Procedimentos que funcionaram:** fluxos reproduzíveis com sucesso comprovado.
- **Correções do usuário:** mudanças solicitadas explicitamente e o motivo subjacente.
- **Erros de compilação ou execução:** mensagens exatas de erro, incompatibilidades de sintaxe, tipos ou bibliotecas.
- **Armadilhas técnicas (pegadinhas):** comportamentos contraintuitivos do ambiente, corretora, dados ou ferramentas.
- **Decisões metodológicas:** critérios estatísticos, períodos, universos e premissas financeiras adotadas.
- **Falsos positivos / Tentativas descartadas:** caminhos que pareciam promissores mas falharam nos testes.

> **Regra de ouro:** Diferencie fatos verificados (código testado, saída real de terminal) de estimativas ou hipóteses não comprovadas. Nunca invente causas ou resultados.

## 2. Direcionar para o Destino Correto

| Tipo de Informação | Destino Principal | Formato / Estrutura |
|---|---|---|
| **Procedimento técnico reutilizável** (compilação CLI, testes estatísticos, coletores) | `~/.claude/skills/<nome>/SKILL.md` ou `.claude/skills/<nome>/SKILL.md` | Skill acionável com YAML frontmatter (`name`, `description`) e regras imperativas. |
| **Histórico e aprendizados do projeto** (decisões, vieses, limitações de dados) | `.codex/memory/aprendizados.md` | Seções temáticas com causas confirmadas, correções e evidências locais. |
| **Estado do projeto e passagem de bastão** (entregas, commits, pendências) | `.codex/memory/bastao-codex.md` | Resumo único sobrescrito: data, entregas, commit hash, pendências e frase de retomada. |
| **Orientações de navegação do repositório** | `AGENTS.md` | Apontamento curto e fixo para os arquivos de memória. |

## 3. Padrão de Registro de Lições e Armadilhas

Para cada lição, erro ou pegadinha relevante, registre no formato enxuto:
> **[Contexto/Sintoma]** $\to$ **[Causa Confirmada]** $\to$ **[Correção Efetuada]** $\to$ **[Regra de Prevenção]** $\to$ **[Evidência/Arquivo]**

### Exemplo:
- **Sintoma:** MetaEditor retorna `error 294: arrays are passed by reference only`.
- **Causa:** No MQL5, parâmetros do tipo array não podem ser passados por valor (`string arr[]`).
- **Correção:** Adicionar o operador de referência `&` na assinatura (`string &arr[]`).
- **Prevenção:** Sempre passar arrays por referência em funções MQL5.
- **Evidência:** [`B3Swing_C_RelativeStrength.mq5`](file:///Y:/Claude/MCP_MT5/MQL5/Experts/B3Swing/B3Swing_C_RelativeStrength.mq5).

## 4. Criação de Novas Skills
Se a sessão desenvolveu um fluxo novo que se repetirá em outros projetos ou tarefas:
1. Crie uma pasta `skills/<nome-da-skill>/` contendo `SKILL.md`.
2. Inclua frontmatter YAML com `name` e `description` rica em gatilhos de invocação.
3. Foque em procedimentos operacionais, armadilhas conhecidas e comandos de validação.
4. Mantenha parâmetros específicos do projeto isolados nos exemplos ou em `references/`.

## 5. Fechamento e Entrega
Após salvar os registros:
1. Mostre um sumário em tabela: `Arquivo modificado/criado | O que foi registrado`.
2. Destaque erros e pegadinhas documentados nesta sessão.
3. Informe pendências reais que dependem de autorização ou dados futuros.
4. Forneça uma frase acionável para retomar o trabalho na próxima sessão.
