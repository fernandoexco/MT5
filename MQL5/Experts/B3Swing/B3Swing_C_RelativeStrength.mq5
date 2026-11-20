//+------------------------------------------------------------------+
//|                                B3Swing_C_RelativeStrength.mq5   |
//|             Estrategia C: Swing Trade com Forca Relativa e Canal  |
//|                             MetaTrader 5 Strategy Tester Only    |
//+------------------------------------------------------------------+
#property strict
#property version   "1.00"
#property description "Swing Trade B3: Forca Relativa, Canal de Alta e Gestao Matematica de Risco; Strategy Tester only."

#include "B3SwingCommon.mqh"

input double InpStartingCapitalBRL        = 500.00;   // Capital inicial da conta (R$)
input double InpRiskPerTradePercent       = 0.5;      // Risco maximo por operacao (% patrimonio)
input double InpMaxAggRiskPercent         = 1.5;      // Risco maximo agregado (% patrimonio)
input double InpPreventiveLossPercent      = 6.0;      // Drawdown preventivo (% sobre topo)
input double InpSuspendLossPercent         = 10.0;     // Drawdown de suspensao (% sobre topo)
input double InpFeeRatePerSide             = 0.0005;   // Taxa variavel por lado (0,05%)
input double InpFixedFeePerSideBRL         = 0.05;     // Custo fixo por lado (R$ 0,05)
input int    InpStopSlippageTicks           = 2;        // Slippage estressado do stop (ticks)
input int    InpATRPeriod                   = 14;       // Periodo do ATR
input double InpATRStopMultiplier           = 2.0;      // Multiplicador do ATR para stop
input int    InpRegressionPeriod             = 120;      // Periodo da regressao log-linear
input int    InpFastMAPeriod                 = 50;       // Periodo da media rapida (SMA50)
input int    InpSlowMAPeriod                 = 200;      // Periodo da media lenta (SMA200)
input int    InpMAPrevOffset                 = 10;       // Offset para SMA50 ascendente
input int    InpRS20Period                   = 20;       // Periodo RS curto
input int    InpRS60Period                   = 60;       // Periodo RS medio
input int    InpRS120Period                  = 120;      // Periodo RS longo
input double InpWeightRS20                  = 0.40;     // Peso RS20 no SCORE
input double InpWeightRS60                  = 0.35;     // Peso RS60 no SCORE
input double InpWeightRS120                 = 0.25;     // Peso RS120 no SCORE
input string InpUniverse                    = "ITUB4,BBAS3,WEGE3,GGBR4,PETR4,VALE3,BBDC4,ABEV3,EGIE3,SUZB3";
input string InpBenchmarkSymbol              = "IBOV";
input long   InpMagicNumber                  = 8101203;

int      g_atrHandle   = INVALID_HANDLE;
datetime g_lastBarTime = 0;
bool     g_suspended   = false;
double   g_peakEquity  = 500.00;
CTrade   g_trade;

struct UniverseCandidate
{
   string symbol;
   double rs20;
   double rs60;
   double rs120;
   double p20;
   double p60;
   double p120;
   double score;
   double atrRatio;
   bool   hasHistory;
   bool   eligible;
};

//+------------------------------------------------------------------+
//| Medias e regressao                                               |
//+------------------------------------------------------------------+
double MeanCloseShift(const MqlRates &rates[], const int firstShift, const int count)
{
   double total = 0.0;
   for(int shift = firstShift; shift < firstShift + count; ++shift)
      total += rates[shift].close;
   return total / count;
}

bool GetATR(double &atr)
{
   double values[];
   ArraySetAsSeries(values, true);
   if(CopyBuffer(g_atrHandle, 0, 1, 1, values) != 1)
      return false;
   atr = values[0];
   return atr > 0.0;
}

bool CalculateRegression(const MqlRates &rates[],
                         const int period,
                         double &slope,
                         double &intercept,
                         double &sigma)
{
   double closes[];
   ArrayResize(closes, period);
   double meanY = 0.0;
   for(int i = 0; i < period; ++i)
   {
      const int shift = period - i;
      if(rates[shift].close <= 0.0)
         return false;
      closes[i] = MathLog(rates[shift].close);
      meanY += closes[i];
   }
   meanY /= period;

   const double meanX = (period - 1.0) / 2.0;
   double cov = 0.0;
   double varX = 0.0;
   for(int i = 0; i < period; ++i)
   {
      cov += (i - meanX) * (closes[i] - meanY);
      varX += (i - meanX) * (i - meanX);
   }
   if(varX <= 0.0)
      return false;

   slope = cov / varX;
   intercept = meanY - slope * meanX;
   double sumRes = 0.0;
   for(int i = 0; i < period; ++i)
   {
      const double res = closes[i] - intercept - slope * i;
      sumRes += res * res;
   }
   sigma = MathSqrt(sumRes / (period - 2.0));
   return true;
}

//+------------------------------------------------------------------+
//| Gestao de Drawdown sobre o topo (High-Water Mark)                |
//+------------------------------------------------------------------+
bool ManagePeakDrawdown(bool &suspended)
{
   if(!MQLInfoInteger(MQL_TESTER))
      return false;

   const double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity > g_peakEquity)
      g_peakEquity = equity;

   const double dd = (g_peakEquity > 0.0 ? (g_peakEquity - equity) / g_peakEquity : 0.0);

   if(dd >= InpSuspendLossPercent / 100.0)
   {
      suspended = true;
      if(B3OwnPosition(InpMagicNumber))
      {
         if(!g_trade.PositionClose(_Symbol))
            PrintFormat("Falha ao liquidar posicao por Drawdown de Suspensao (%.2f%%): %u",
                        dd * 100.0, g_trade.ResultRetcode());
         else
            PrintFormat("Posicao liquidada por Drawdown de Suspensao: %.2f%%", dd * 100.0);
      }
      return false;
   }

   if(suspended || dd >= InpPreventiveLossPercent / 100.0)
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| Dimensionamento de posicao percentual sobre patrimonio           |
//+------------------------------------------------------------------+
bool CalculateVolumeC(const double entryPrice,
                      const double stopPrice,
                      double &volume)
{
   if(!MQLInfoInteger(MQL_TESTER) || entryPrice <= 0.0 || stopPrice <= 0.0 ||
      stopPrice >= entryPrice)
      return false;

   const double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   const double contractSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
   const double minVolume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   const double volumeStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   const double maxVolume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(tickSize <= 0.0 || contractSize <= 0.0 || minVolume <= 0.0 ||
      volumeStep <= 0.0 || maxVolume < minVolume)
      return false;

   const double currentEquity = MathMax(0.0, AccountInfoDouble(ACCOUNT_EQUITY));
   const double maxTradeRisk = currentEquity * (InpRiskPerTradePercent / 100.0);
   const double maxAggRisk = currentEquity * (InpMaxAggRiskPercent / 100.0);

   // Calcular risco estimado por acao
   const double stressedStop = MathMax(tickSize, stopPrice - InpStopSlippageTicks * tickSize);
   const double riskPerShare = (entryPrice - stressedStop) + (entryPrice + stressedStop) * InpFeeRatePerSide;
   const double fixedFees = 2.0 * InpFixedFeePerSideBRL;

   if(maxTradeRisk <= fixedFees || riskPerShare <= 0.0)
      return false;

   const double availableRisk = MathMin(maxTradeRisk, maxAggRisk);
   const double qRisk = (availableRisk - fixedFees) / riskPerShare;

   const double availableCash = MathMax(0.0, AccountInfoDouble(ACCOUNT_MARGIN_FREE));
   const double notionalPerShare = entryPrice * (1.0 + InpFeeRatePerSide);
   const double qCash = (availableCash - InpFixedFeePerSideBRL) / notionalPerShare;

   const double rawVolume = MathMin(MathMin(qRisk, qCash), maxVolume);
   volume = MathFloor(rawVolume / volumeStep + 1e-10) * volumeStep;
   volume = NormalizeDouble(volume, 8);

   if(volume < minVolume)
      return false;

   return true;
}

//+------------------------------------------------------------------+
//| Ranking de Forca Relativa e Verificacao TOP 3                    |
//+------------------------------------------------------------------+
bool IsSymbolInTop3(string &universeSymbols[], const int uCount, const datetime asOfTime)
{
   UniverseCandidate candidates[];
   ArrayResize(candidates, uCount);

   const int benchShift = iBarShift(InpBenchmarkSymbol, PERIOD_D1, asOfTime, true);
   if(benchShift < 0)
      return false;

   const double bNow = iClose(InpBenchmarkSymbol, PERIOD_D1, benchShift);
   const double b20 = iClose(InpBenchmarkSymbol, PERIOD_D1, benchShift + InpRS20Period);
   const double b60 = iClose(InpBenchmarkSymbol, PERIOD_D1, benchShift + InpRS60Period);
   const double b120 = iClose(InpBenchmarkSymbol, PERIOD_D1, benchShift + InpRS120Period);

   if(bNow <= 0.0 || b20 <= 0.0 || b60 <= 0.0 || b120 <= 0.0)
      return false;

   const double bRet20 = bNow / b20 - 1.0;
   const double bRet60 = bNow / b60 - 1.0;
   const double bRet120 = bNow / b120 - 1.0;

   int validCount = 0;
   for(int u = 0; u < uCount; ++u)
   {
      candidates[u].symbol = universeSymbols[u];
      candidates[u].hasHistory = false;
      candidates[u].eligible = false;

      const int symShift = iBarShift(universeSymbols[u], PERIOD_D1, asOfTime, true);
      if(symShift < 0)
         continue;

      MqlRates symRates[];
      ArraySetAsSeries(symRates, true);
      const int needBars = InpSlowMAPeriod + InpMAPrevOffset + 5;
      if(CopyRates(universeSymbols[u], PERIOD_D1, symShift, needBars, symRates) < needBars)
         continue;

      const double sNow = symRates[0].close;
      const double s20 = symRates[InpRS20Period].close;
      const double s60 = symRates[InpRS60Period].close;
      const double s120 = symRates[InpRS120Period].close;

      if(sNow <= 0.0 || s20 <= 0.0 || s60 <= 0.0 || s120 <= 0.0)
         continue;

      candidates[u].rs20 = (sNow / s20 - 1.0) - bRet20;
      candidates[u].rs60 = (sNow / s60 - 1.0) - bRet60;
      candidates[u].rs120 = (sNow / s120 - 1.0) - bRet120;
      candidates[u].hasHistory = true;

      // Filtros obrigatorios:
      // RS20 > 0, RS60 > 0, Fechamento > SMA50, SMA50 > SMA200, SMA50 atual > SMA50 de 10 pregoes atras
      const double sma50 = MeanCloseShift(symRates, 0, InpFastMAPeriod);
      const double sma200 = MeanCloseShift(symRates, 0, InpSlowMAPeriod);
      const double sma50_prev10 = MeanCloseShift(symRates, InpMAPrevOffset, InpFastMAPeriod);

      // ATR(14)
      double trSum = 0.0;
      for(int k = 0; k < 14; ++k)
      {
         const double h = symRates[k].high;
         const double l = symRates[k].low;
         const double pc = symRates[k + 1].close;
         trSum += MathMax(h - l, MathMax(MathAbs(h - pc), MathAbs(l - pc)));
      }
      const double symATR = trSum / 14.0;
      candidates[u].atrRatio = (sNow > 0.0 ? symATR / sNow : 999.0);

      if(candidates[u].rs20 > 0.0 && candidates[u].rs60 > 0.0 &&
         sNow > sma50 && sma50 > sma200 && sma50 > sma50_prev10)
      {
         candidates[u].eligible = true;
      }
      validCount++;
   }

   if(validCount < uCount)
      return false;

   // Calcular percentis transversais das 3 medidas no universo elegivel
   // Pct = rank / (N - 1) * 100
   for(int i = 0; i < uCount; ++i)
   {
      int countLess20 = 0, countLess60 = 0, countLess120 = 0;
      for(int j = 0; j < uCount; ++j)
      {
         if(candidates[j].rs20 < candidates[i].rs20) countLess20++;
         if(candidates[j].rs60 < candidates[i].rs60) countLess60++;
         if(candidates[j].rs120 < candidates[i].rs120) countLess120++;
      }
      candidates[i].p20 = ((double)countLess20 / (uCount - 1.0)) * 100.0;
      candidates[i].p60 = ((double)countLess60 / (uCount - 1.0)) * 100.0;
      candidates[i].p120 = ((double)countLess120 / (uCount - 1.0)) * 100.0;
      candidates[i].score = InpWeightRS20 * candidates[i].p20 +
                            InpWeightRS60 * candidates[i].p60 +
                            InpWeightRS120 * candidates[i].p120;
   }

   // Ordenar candidatos elegiveis por SCORE decrescente
   // Desempate: 1. Menor ATR14/fechamento; 2. Ticker ordem alfabetica
   int eligibleIndices[];
   int eligibleTotal = 0;
   for(int i = 0; i < uCount; ++i)
   {
      if(candidates[i].eligible)
      {
         ArrayResize(eligibleIndices, eligibleTotal + 1);
         eligibleIndices[eligibleTotal] = i;
         eligibleTotal++;
      }
   }

   if(eligibleTotal == 0)
      return false;

   // Bubble sort simples para elegiveis
   for(int i = 0; i < eligibleTotal - 1; ++i)
   {
      for(int j = 0; j < eligibleTotal - 1 - i; ++j)
      {
         const int a = eligibleIndices[j];
         const int b = eligibleIndices[j + 1];
         bool swap = false;
         if(candidates[a].score < candidates[b].score)
            swap = true;
         else if(MathAbs(candidates[a].score - candidates[b].score) < 1e-9)
         {
            if(candidates[a].atrRatio > candidates[b].atrRatio)
               swap = true;
            else if(MathAbs(candidates[a].atrRatio - candidates[b].atrRatio) < 1e-9)
            {
               if(candidates[a].symbol > candidates[b].symbol)
                  swap = true;
            }
         }
         if(swap)
         {
            const int tmp = eligibleIndices[j];
            eligibleIndices[j] = eligibleIndices[j + 1];
            eligibleIndices[j + 1] = tmp;
         }
      }
   }

   // Verificar se _Symbol esta no TOP 3
   const int topN = MathMin(3, eligibleTotal);
   for(int k = 0; k < topN; ++k)
   {
      if(candidates[eligibleIndices[k]].symbol == _Symbol)
         return true;
   }

   return false;
}

//+------------------------------------------------------------------+
//| Sinal da Estrategia C                                            |
//+------------------------------------------------------------------+
bool StrategyCSignal(MqlRates &rates[], string &universeSymbols[], const int uCount, double &atr)
{
   if(!GetATR(atr))
      return false;

   // 1. Ativo entre os 3 melhores do ranking no fechamento de D-1
   if(!IsSymbolInTop3(universeSymbols, uCount, rates[1].time))
      return false;

   // 2. Canal de alta valido
   double slope = 0.0, intercept = 0.0, sigma = 0.0;
   if(!CalculateRegression(rates, InpRegressionPeriod, slope, intercept, sigma))
      return false;
   if(slope <= 0.0 || sigma <= 1e-12)
      return false;

   const double maFast = MeanCloseShift(rates, 1, InpFastMAPeriod);
   const double maFastPrev = MeanCloseShift(rates, 1 + InpMAPrevOffset, InpFastMAPeriod);
   const double maSlow = MeanCloseShift(rates, 1, InpSlowMAPeriod);

   if(maFast <= maSlow || maFast <= maFastPrev || rates[1].close <= maSlow)
      return false;

   // 3. Preco na zona de entrada: Fechamento entre banda inferior e linha central
   const double center = MathExp(intercept + slope * (InpRegressionPeriod - 1));
   const double lower = MathExp(intercept + slope * (InpRegressionPeriod - 1) - 2.0 * sigma);
   const double upper = MathExp(intercept + slope * (InpRegressionPeriod - 1) + 2.0 * sigma);

   const bool inZone = (rates[1].close >= lower && rates[1].close <= center);

   // 4. Recuperacao confirmada: Fechamento atual > maxima do candle anterior
   const bool confirmed = (rates[1].close > rates[2].high);

   // Nao comprar acima da banda superior
   const bool notAboveUpper = (rates[1].close <= upper);

   return inZone && confirmed && notAboveUpper;
}

//+------------------------------------------------------------------+
//| Gestao de Posicao Aberta: Stops e Saidas                         |
//+------------------------------------------------------------------+
void ManageOpenPositionC(MqlRates &rates[], const double atr)
{
   if(!B3OwnPosition(InpMagicNumber))
      return;

   // Saida adicional: Fechamento abaixo da SMA50 ou Inclinacao do canal <= 0
   const double maFast = MeanCloseShift(rates, 1, InpFastMAPeriod);
   double slope = 0.0, intercept = 0.0, sigma = 0.0;
   CalculateRegression(rates, InpRegressionPeriod, slope, intercept, sigma);

   const bool exitSignal = (rates[1].close < maFast) || (slope <= 0.0);
   if(exitSignal)
   {
      if(!g_trade.PositionClose(_Symbol))
         PrintFormat("Falha ao encerrar posicao por sinal de saida: %u", g_trade.ResultRetcode());
      else
         Print("Posicao encerrada por sinal de saida (fechamento < SMA50 ou inclinacao <= 0).");
      return;
   }

   // Stop movel: Maximo entre stop anterior e maior fechamento desde a entrada - 2 * ATR
   // O stop nunca podera ser afastado.
   const datetime posTime = (datetime)PositionGetInteger(POSITION_TIME);
   const int entryShift = iBarShift(_Symbol, PERIOD_D1, posTime, false);
   if(entryShift >= 1 && atr > 0.0)
   {
      double maxClose = rates[1].close;
      for(int shift = 1; shift <= entryShift; ++shift)
         maxClose = MathMax(maxClose, rates[shift].close);

      const double candidateStop = B3RoundDownToTick(maxClose - atr * InpATRStopMultiplier);
      const double currentStop = PositionGetDouble(POSITION_SL);

      if(candidateStop > currentStop)
         B3RaiseStop(g_trade, candidateStop);
   }
}

//+------------------------------------------------------------------+
//| OnInit                                                           |
//+------------------------------------------------------------------+
int OnInit()
{
   if(InpStartingCapitalBRL <= 0.0 || InpRiskPerTradePercent <= 0.0 ||
      InpMaxAggRiskPercent <= 0.0 || InpPreventiveLossPercent <= 0.0 ||
      InpSuspendLossPercent <= InpPreventiveLossPercent ||
      InpATRPeriod < 2 || InpATRStopMultiplier <= 0.0 ||
      InpRegressionPeriod < 10 || InpFastMAPeriod < 2 || InpSlowMAPeriod <= InpFastMAPeriod ||
      InpBenchmarkSymbol == "" || InpFeeRatePerSide < 0.0 ||
      InpFixedFeePerSideBRL < 0.0 || InpStopSlippageTicks < 0)
   {
      Print("Parametros incorretos para B3Swing_C.");
      return INIT_PARAMETERS_INCORRECT;
   }

   if(!B3TesterReady(InpStartingCapitalBRL, InpBenchmarkSymbol))
      return INIT_FAILED;

   // Habilitar simbolos do universo no Market Watch
   string syms[];
   const int count = StringSplit(InpUniverse, ',', syms);
   for(int i = 0; i < count; ++i)
      SymbolSelect(syms[i], true);

   g_atrHandle = iATR(_Symbol, PERIOD_D1, InpATRPeriod);
   if(g_atrHandle == INVALID_HANDLE)
   {
      Print("Falha ao criar handle iATR.");
      return INIT_FAILED;
   }

   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   g_peakEquity = InpStartingCapitalBRL;
   g_suspended = false;

   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| OnDeinit                                                         |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(g_atrHandle != INVALID_HANDLE)
      IndicatorRelease(g_atrHandle);
}

//+------------------------------------------------------------------+
//| OnTick                                                           |
//+------------------------------------------------------------------+
void OnTick()
{
   if(!MQLInfoInteger(MQL_TESTER))
      return;

   // Gerenciar perdas e travas de Drawdown sobre o High-Water Mark
   const bool entriesAllowed = ManagePeakDrawdown(g_suspended);
   if(g_suspended)
      return;

   if(!B3NewDailyBar(g_lastBarTime))
      return;

   const int requiredBars = MathMax(InpSlowMAPeriod + InpMAPrevOffset + 5,
                                    InpRegressionPeriod + 5);
   MqlRates rates[];
   if(!B3ReadRates(requiredBars, rates))
      return;

   double atr = 0.0;
   GetATR(atr);

   // Gestao de posicoes abertas (saidas por sinal e stop movel)
   ManageOpenPositionC(rates, atr);

   if(!entriesAllowed || B3OwnPosition(InpMagicNumber) || PositionsTotal() >= 3)
      return;

   string universeSymbols[];
   const int uCount = StringSplit(InpUniverse, ',', universeSymbols);
   if(uCount < 10)
      return;

   // Sinal de entrada C
   if(!StrategyCSignal(rates, universeSymbols, uCount, atr))
      return;

   const double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   const double stop = B3RoundDownToTick(ask - atr * InpATRStopMultiplier);
   if(stop <= 0.0 || stop >= ask)
      return;

   double volume = 0.0;
   if(!CalculateVolumeC(ask, stop, volume))
   {
      Print("Entrada descartada: lote minimo excede risco ou capital disponivel.");
      return;
   }

   if(!g_trade.Buy(volume, _Symbol, 0.0, stop, 0.0, "B3 Swing C - RS & Channel"))
      PrintFormat("Ordem de compra rejeitada no Tester: %u", g_trade.ResultRetcode());
   else
      PrintFormat("Ordem de compra executada no Tester: %s Lote=%.2f Preco=%.2f SL=%.2f",
                  _Symbol, volume, ask, stop);
}
//+------------------------------------------------------------------+
