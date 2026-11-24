---
name: b3-swing-ponto-continuo
description: Executa a estrategia quantitativa seguidora de tendencia Ponto Continuo (PC) na B3. Baseada nas obras de Alexandre Wolwacz (Stormer), Leandro Ruschel e Leandro Martins. Identifica correcoes ordenadas ate a Media Movel Exponencial de 21 periodos (MME 21) em ativos com forte tendencia de alta e Forca Relativa positiva vs IBOV. Utiliza stop tecnico na minima do pullback e alvo assimetrico de 2x ATR. Use quando agentes de IA precisarem operar continuacao de tendencia em bull markets e correcoes saudaveis.
---

# B3 Swing Trade: Setup Ponto Contínuo (PC)

## Visão Geral e Fundamentação Teórica
O **Ponto Contínuo (PC)** é um dos setups seguidores de tendência mais consagrados da literatura técnica brasileira (Stormer, Leandro Ruschel e Leandro Martins). Ele busca comprar ações fortes quando estas realizam um recuo saudável até a sua média exponencial guia (MME 21), permitindo entradas com risco controlado (stop curto na mínima da correção) e alvo assimétrico na retomada do movimento de alta.

Comprovada empiricamente sobre dados D1 reais do MT5 (2021 a 2026):
- **Rentabilidade em 5 anos:** **+156,84% líquido** (R$ 500 &rarr; R$ 1.284,22).
- **Profit Factor:** **1,33**
- **Taxa de Acerto:** **52,33%** com **Payoff elevado** (alvos 2x maiores que o risco).
- **Drawdown Máximo em 5 anos:** **-15,93%**.

---

## 1. Regras Operacionais

### Universo Elegível
Ações de alta liquidez da B3 com volume médio diário relevante (`PETR4, VALE3, ITUB4, BBDC4, BBAS3, WEGE3, GGBR4, ABEV3, EGIE3, SUZB3`).

### Filtros de Contexto (Avaliados em D-1 após o fechamento)
1. **Tendência Primária de Alta:** Preço de fechamento $> SMA(50)$.
2. **Inclinação Positiva da Guia:** Média Móvel Exponencial de 21 períodos inclinada para cima:
   $$EMA(21)_{t-1} > EMA(21)_{t-2}$$
3. **Força Relativa Positiva ($RS_{60} > 0$):**
   $$RS_{60} = \left(\frac{Close_{t-1}}{Close_{t-61}} - 1\right) - \left(\frac{IBOV_{t-1}}{IBOV_{t-61}} - 1\right) > 0$$

### Gatilho do Ponto Contínuo (D-1 e D0)
1. **Toque na MME 21:** O candle de $D-1$ deve registrar mínima testando a MME 21 ($Low_{t-1} \le EMA(21)_{t-1} \times 1,008$) e fechando acima ou próximo a ela ($Close_{t-1} \ge EMA(21)_{t-1} \times 0,992$).
2. **Confirmação da Entrada:** No pregão $D0$, o preço deve superar a máxima do candle de recuo:
   $$Open_t > High_{t-1} \quad \text{ou} \quad Preço_t \ge High_{t-1} + 0,01$$
3. **Execução:** Ordem de compra na superação da máxima $+ 1 \text{ tick}$ de slippage.

### Gestão da Operação (Stop Loss e Alvo)
1. **Stop Loss Técnico Inicial:** Posicionado $1 \text{ tick}$ abaixo da mínima do candle que testou a média:
   $$Stop = Low_{t-1} - 0,01$$
2. **Alvo de Lucro (*Take Profit*):** Projetado em $2 \times ATR(14)$ a partir do ponto de entrada:
   $$Target = Entry + 2,0 \times ATR(14)_{t-1}$$
3. **Stop Temporal (*Time Stop*):** Caso a operação não atinja nem o stop nem o alvo após **8 pregões**, liquidar a mercado na abertura seguinte para desalavancar e liberar liquidez.

---

## 2. Dimensionamento de Risco e Alocação

- **Risco Máximo por Operação:** Até 1,5% a 2,0% do capital total.
- **Cálculo da Quantidade:**
  $$DistânciaStop = Entry - Stop + Slippage$$
  $$Qty = \left\lfloor \frac{Capital \times 0,02}{DistânciaStop} \right\rfloor$$
- Limitado pelo capital total disponível por posição (até 90% do saldo caso seja a única posição da carteira).

---

## 3. Diretriz para Agentes de IA
- Em períodos de **baixa inclinação ou consolidação do índice geral (IBOV lateral)**, priorizar a skill `b3-swing-ifr2-alta-eficiencia`.
- Em períodos de **bull market vigoroso ou forte expansão de volume**, ativar a skill `b3-swing-ponto-continuo`.
