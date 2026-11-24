---
name: mql5-b3-quant-tester
description: Desenvolvimento, compilação via MetaEditor CLI e validação quantitativa de Expert Advisors (MQL5) para swing trade na B3. Cobre integração com simulador Python multiativo, travas de drawdown High-Water Mark, limitações de lote da Clear MT5 e testes estatísticos de robustez. Use ao criar EAs MQL5, compilar .mq5, simular carteiras B3 ou rodar backtests quantitativos.
---

# Desenvolvimento e Validação Quantitativa de EAs MQL5 para B3

Guia prático para desenvolver, compilar e auditar estratégias automatizadas de swing trade em MQL5 e motores externos de simulação na B3.

## 1. Arquitetura do Expert Advisor MQL5

### Estrutura Base
- Separe lógicas comuns (funções de lote, travas de tester, utilitários de tick) em um cabeçalho reutilizável: `B3SwingCommon.mqh`.
- Estruture o EA (`.mq5`) em:
  - `OnInit()`: Validação estrita de parâmetros, criação de handles de indicadores (`iATR`, etc.), verificação de ambiente.
  - `OnDeinit()`: Liberação obrigatória de handles via `IndicatorRelease()`.
  - `OnTick()`: Avaliação no fechamento da barra D1 (`B3NewDailyBar`), gestão de stops móveis e execução de ordens.

### Bloqueio Mandatório de Ordens Reais
Em projetos exploratórios ou de pesquisa, **nunca permita envio acidental de ordens reais**. Insira no topo de `OnInit()` e `OnTick()`:
```cpp
if(!MQLInfoInteger(MQL_TESTER))
{
   Print("Execução bloqueada: este EA funciona exclusivamente no Strategy Tester.");
   return INIT_FAILED; // ou return no OnTick
}
```

### Validação de Conta no Tester
```cpp
if(MathAbs(AccountInfoDouble(ACCOUNT_BALANCE) - startingCapital) > 0.01 ||
   AccountInfoString(ACCOUNT_CURRENCY) != "BRL")
{
   Print("Conta de teste deve possuir saldo e moeda exatos da simulação.");
   return INIT_FAILED;
}
```

---

## 2. Armadilhas Técnicas de MQL5 (Pegadinhas Comuns)

### Pegadinha 1: Passagem de Arrays por Referência (`error 294`)
- **Sintoma:** O MetaEditor falha na compilação com `error 294: arrays are passed by reference only`.
- **Causa:** No MQL5, parâmetros do tipo array **não podem ser passados por valor**.
- **Solução:** Adicione sempre o `&` antes do nome do array no parâmetro:
  ```cpp
  // INCORRETO:
  bool StrategySignal(MqlRates rates[], string universeSymbols[], int count);

  // CORRETO:
  bool StrategySignal(MqlRates &rates[], string &universeSymbols[], const int count);
  ```

### Pegadinha 2: Normalização de Preço por Tick Size
- Preços de ordens e stops devem ser múltiplos exatos do tick size da B3 (R$ 0,01):
  ```cpp
  double RoundDownToTick(const double price)
  {
     const double tick = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
     if(tick <= 0.0) return 0.0;
     return NormalizeDouble(MathFloor(price / tick + 1e-10) * tick, _Digits);
  }
  ```

### Pegadinha 3: Ausência de Símbolos Fracionários no Servidor MT5 (ex: Clear)
- **Sintoma:** O Strategy Tester recusa abrir ordens em contas pequenas (R$ 500) com: `Simbolo nao habilita lote fracionario de ate uma acao por volume minimo`.
- **Causa:** O servidor Clear MT5 disponibiliza apenas lotes padrão de 100 ações para ações à vista (não há ativos com terminação `F` cadastrados na árvore do servidor).
- **Solução:** Manter a trava de proteção no EA MQL5 (não falsear o lote mínimo) e conduzir o backtest multiativo de carteira com saldo compartilhado e ações unitárias através do simulador Python consolidado.

---

## 3. Compilação Headless via MetaEditor CLI (Windows)

Compile e capture erros diretamente pelo PowerShell sem abrir a interface gráfica:
```powershell
& "C:\Program Files\Clear Investimentos MT5 Terminal\MetaEditor64.exe" /compile:"Y:\Claude\MCP_MT5\MQL5\Experts\B3Swing\SeuEA.mq5" /log:"compile.log"
Start-Sleep -Seconds 2
Get-Content "compile.log"
```
Verifique sempre a saída: `Result: 0 errors, 0 warnings`.

---

## 4. Simulador Python Multiativo: Paridade e Causalidade Estrita

Quando testar uma carteira consolidada de ativos com caixa único (ex: R$ 500 e até 3 posições simultâneas):
1. **Ausência de Look-Ahead:** Sinais devem ser gerados em $t-1$ usando dados fechados. Execução ocorre na abertura de $t$.
2. **Gap de Abertura:** Recalcule a quantidade e o risco usando o preço executável real de abertura (`Ask = Open + slippage`). Se o gap inflacionar o risco ou faltar saldo, descarte a entrada.
3. **Execução de Stop com Gap Intradiário:**
   ```python
   if bar['low'] <= pos['stop']:
       px = min(pos['stop'], bar['open']) - stop_slippage
       px = max(px, TICK)
       # fecha no gap se abriu abaixo do stop
   ```
4. **Drawdown sobre o High-Water Mark:**
   Calcule o drawdown sempre sobre o maior patrimônio consolidado atingido:
   ```python
   peak_equity = max(peak_equity, eq_open)
   dd = (peak_equity - eq_open) / peak_equity
   if dd >= 0.10: # suspensao e liquidacao
       ...
   elif dd >= 0.06: # suspensao de novas entradas
       ...
   ```
5. **Divisão por Zero em Percentis Transversais:**
   Ao rodar avaliações isoladas de um único ativo (`n_pool <= 1`):
   ```python
   if n_pool <= 1:
       pct = {sym: 100.0}
   else:
       pct = {s: rank / (n_pool - 1) * 100 for rank, s in enumerate(sorted_syms)}
   ```

---

## 5. Bateria Estatística de Robustez Obrigatória

Qualquer estratégia antes de ser considerada para paper trading deve passar por:
1. **Estresse de Custos e Slippage:**
   - Base: 0,05%/lado + R$ 0,05 fixo; slip 1 tick entrada, 2 ticks stop.
   - Custos $2\times$ e $4\times$.
   - Slippage $3\times$.
   - Cenário combinado: Custos $2\times$ + Slippage $3\times$.
2. **Leave-One-Out por Ativo:** Testar a carteira excluindo 1 ativo de cada vez (garante que o retorno não depende de uma única ação isolada).
3. **Análise de Concentração de Lucros:** Verificar o impacto das 3 maiores operações. Se `Lucro Total - Top 3 < 0`, a estratégia é dependente de outliers e frágil.
4. **Bootstrap da Expectativa Matemática:**
   - 5.000 iterações com reposição sobre os PnLs das operações fechadas.
   - Obter intervalo de confiança de 95% ($2{,}5\%$ a $97{,}5\%$).
   - Se o IC 95% cruzar o zero (conter valores negativos), **a hipótese nula de vantagem zero não pode ser rejeitada estatisticamente**.
5. **Comparação com Benchmarks:** Comparar no mesmo período com CDI e Ibovespa/BOVA11. Retornos nominais positivos que perdem para o CDI com folga representam custo de oportunidade negativo para swing trade em ações.

---

## 6. Critérios Formais de Classificação

- **APROVADA PARA PAPER TRADING:** Retorno líquido robusto, bate CDI/IBOV, IC 95% da expectativa estritamente $> 0$, sobrevive a custos $2\times$ + slippage $3\times$, lucro consistente sem dependência de outliers e controles de risco funcionais.
- **REVISÃO NECESSÁRIA:** Resultados líquidos positivos e risco controlado, mas amostra pequena ($< 100$ trades), IC 95% inclui zero, sensível a custos ou dependente de poucas operações excepcionais.
- **REPROVADA:** Prejuízo persistente, drawdown incontrolável ou falhas graves de execução/risco.
