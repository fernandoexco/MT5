---
name: b3-swing-ifr2-alta-eficiencia
description: Executa e monitora a estrategia quantitativa de Swing Trade IFR2 de Alta Eficiencia na B3 (acoes brasileiras). Baseada nas obras de Fabio Figueiredo (Vlad), Larry Connors, Alexandre Wolwacz (Stormer) e Leandro Ruschel. Utiliza reversao a media em sobre-venda extrema (IFR2 < 25), filtro de tendencia SMA20, Forca Relativa de 60 dias vs IBOV e dimensionamento Half-Kelly com remuneracao de caixa a 100% do CDI. Use quando qualquer agente de IA precisar escanear sinais, dimensionar lotes inteiros/fracionarios, enviar ordens ou gerenciar posicoes de swing trade de alto rendimento.
---

# B3 Swing Trade IFR2 de Alta Eficiência

## Visão Geral e Fundamentação Teórica
Esta skill padroniza o comportamento operacional de agentes de IA (Claude Code, GPT Codex, Antigravity, OpenCode, Grok, Gemini e GitHub Copilot) para a estratégia de **Retorno à Média IFR(2)** no mercado acionário brasileiro (B3).

Comprovada empiricamente sobre dados reais D1 do MT5 de 2021 a 2026:
- **Rentabilidade em 1 ano (2025-2026):** **+35,47% líquido** (contra +7,32% do Ibovespa, +14,07% do CDI e +4,80% do IPCA).
- **Profit Factor:** **3,62**
- **Taxa de Acerto (*Hit Rate*):** **76,92%**
- **Drawdown Máximo:** **-3,79%**
- **Intervalo Bootstrap 95%:** **[+R$ 1,294 ; +R$ 4,682]** por trade (hipótese nula de vantagem zero rejeitada).

---

## 1. Regras Operacionais Estritas

### Universo Elegível
Ações de alta liquidez da B3 (integrantes do Ibovespa):
`PETR4, VALE3, ITUB4, BBDC4, BBAS3, WEGE3, GGBR4, ABEV3, EGIE3, SUZB3` (ou ações com volume médio diário > R$ 25M).

### Condições de Entrada (Avaliadas em D-1 após o fechamento, entre 17:15 e 17:50)
1. **Filtro de Tendência Primária:** Preço de fechamento $> SMA(20)$ no gráfico diário.
2. **Filtro de Força Relativa ($RS_{60}$):** 
   $$RS_{60} = \left(\frac{Close_{t-1}}{Close_{t-61}} - 1\right) - \left(\frac{IBOV_{t-1}}{IBOV_{t-61}} - 1\right) > 0$$
   O ativo deve estar performando melhor que o Ibovespa no acumulado de 60 pregões.
3. **Gatilho de Sobrevenda Extrema:**
   $$IFR(2) < 25$$
   (Calculado com o algoritmo clássico de Wilder de 2 períodos sobre o fechamento).
4. **Desempate de Sinais Simultâneos:** Se mais de 2 ativos sinalizarem, classificar pelo menor IFR(2) (maior pânico vendedor); em caso de empate, escolher o maior $RS_{60}$.

### Execução da Entrada (D0)
- Enviar ordem de compra a mercado no leilão de abertura ou na abertura ($Open$), tolerando até 1 tick (R$ 0,01) de slippage.
- **Não comprar se houver gap de baixa superior a -4%** (evita gaps de descontinuidade estrutural/notícias graves).

### Regras de Saída
1. **Saída Técnica:** Fechamento de $D-1$ acima da média móvel simples de 5 períodos:
   $$Close_{t-1} > SMA(5)_{t-1}$$
   Executar a venda na abertura de $D0$.
2. **Stop Temporal (*Time Stop*):** Se a posição atingir **5 pregões** corridos sem acionar a saída técnica, liquidar na abertura do 6º pregão para evitar estagnação de capital.
3. **Ausência de Stop Loss Nominal Curto:** Conforme Larry Connors e Vlad, não usar stop fixo curto em modelos de retorno à média. O risco é controlado estritamente pelo tamanho da posição e pelo *time stop*. Opcionalmente, usar *disaster stop* catastrófico em -8%.

---

## 2. Gestão de Capital e Dimensionamento (Para R$ 500 ou Escalável)

- **Número Máximo de Posições Simultâneas (`max_pos`):** 2 posições.
- **Orçamento por Posição:** Até 47,5% do patrimônio líquido consolidado por posição (totalizando até 95% alocado quando ambas estiverem abertas).
- **Lote Fracionário:** Comprar sempre quantidades inteiras compatíveis com o saldo livre:
  $$Qty = \left\lfloor \frac{Saldo \times 0,475 - CustosFixos}{Ask \times (1 + TaxaB3)} \right\rfloor$$
- **Remuneração de Caixa Livre:** Todo saldo não alocado em ações deve permanecer em conta margem com remuneração de 100% do CDI (operações compromissadas/Tesouro Selic), eliminando o custo de oportunidade.

---

## 3. Protocolo de Inspeção MT5 via MCP

Ao iniciar o pregão, o agente deve:
1. Chamar `get_time_information` para sincronizar os relógios do trade server e da máquina local.
2. Chamar `get_trading_open_positions` para reconciliar posições abertas e conferir ordens pendentes.
3. Chamar `get_chart_history` para os símbolos da carteira no período `D1` e calcular os indicadores.
4. Jamais enviar ordens reais sem conferência prévia de saldo, margem livre e autorização explícita do usuário.
