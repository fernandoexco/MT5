#property strict
#property version   "1.00"
#property description "Rompimento de 20 pregoes com volume e forca relativa; Strategy Tester only."

#include "B3SwingCommon.mqh"

input double InpStartingCapitalBRL       = 500.00;
input double InpRiskPerTradeBRL           = 2.50;
input double InpMaxCapitalUsePercent      = 90.0;
input double InpPreventiveLossPercent     = 6.0;
input double InpSuspendLossPercent        = 10.0;
input double InpFeeRatePerSide            = 0.0005;
input double InpFixedFeePerSideBRL        = 0.05;
input int    InpStopSlippageTicks          = 2;
input int    InpATRPeriod                  = 14;
input double InpATRStopMultiplier          = 2.0;
input int    InpBreakoutPeriod              = 20;
input int    InpVolumeAveragePeriod         = 20;
input int    InpRelativeStrengthPeriod      = 60;
input int    InpExitLowPeriod               = 10;
input string InpBenchmarkSymbol             = "IBOV";
input long   InpMagicNumber                 = 8101202;

int      g_atrHandle = INVALID_HANDLE;
datetime g_lastBarTime = 0;
bool     g_suspended = false;
CTrade   g_trade;

bool GetATR(double &atr)
{
   double values[];
   ArraySetAsSeries(values, true);
   if(CopyBuffer(g_atrHandle, 0, 1, 1, values) != 1)
      return false;
   atr = values[0];
   return atr > 0.0;
}

bool BreakoutSignal(MqlRates &rates[], double &atr)
{
   if(!GetATR(atr))
      return false;

   double priorHigh = 0.0;
   for(int shift = 2; shift <= InpBreakoutPeriod + 1; ++shift)
      priorHigh = MathMax(priorHigh, rates[shift].high);

   double volumeTotal = 0.0;
   for(int shift = 2; shift <= InpVolumeAveragePeriod + 1; ++shift)
      volumeTotal += B3RateVolume(rates[shift]);

   const double averageVolume = volumeTotal / InpVolumeAveragePeriod;
   const double signalVolume = B3RateVolume(rates[1]);
   if(averageVolume <= 0.0 || signalVolume <= averageVolume)
      return false;
   if(rates[1].close <= priorHigh)
      return false;

   const int benchmarkShift = iBarShift(InpBenchmarkSymbol, PERIOD_D1,
                                        rates[1].time, true);
   if(benchmarkShift < 0)
      return false;

   const double stockPastClose = rates[1 + InpRelativeStrengthPeriod].close;
   const double stockNowClose = rates[1].close;
   const double benchmarkNowClose = iClose(InpBenchmarkSymbol, PERIOD_D1,
                                           benchmarkShift);
   const double benchmarkPastClose = iClose(InpBenchmarkSymbol, PERIOD_D1,
                                            benchmarkShift + InpRelativeStrengthPeriod);
   if(stockPastClose <= 0.0 || stockNowClose <= 0.0 ||
      benchmarkNowClose <= 0.0 || benchmarkPastClose <= 0.0)
      return false;

   const double stockReturn = stockNowClose / stockPastClose - 1.0;
   const double benchmarkReturn = benchmarkNowClose / benchmarkPastClose - 1.0;
   return stockReturn > benchmarkReturn;
}

double LowestPriorLow(MqlRates &rates[], const int firstShift, const int count)
{
   double lowest = rates[firstShift].low;
   for(int shift = firstShift + 1; shift < firstShift + count; ++shift)
      lowest = MathMin(lowest, rates[shift].low);
   return lowest;
}

void ManageOpenPosition(MqlRates &rates[], const double atr)
{
   if(!B3OwnPosition(InpMagicNumber))
      return;

   const double priorTenDayLow = LowestPriorLow(rates, 2, InpExitLowPeriod);
   const double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(rates[1].close < priorTenDayLow)
   {
      if(!g_trade.PositionClose(_Symbol))
         PrintFormat("Falha ao fechar pela minima de 10 pregoes: %u",
                     g_trade.ResultRetcode());
      return;
   }

   if(atr > 0.0 && bid > PositionGetDouble(POSITION_PRICE_OPEN))
      B3RaiseStop(g_trade, MathMax(priorTenDayLow,
                                   bid - atr * InpATRStopMultiplier));
}

int OnInit()
{
   if(InpStartingCapitalBRL <= 0.0 || InpRiskPerTradeBRL <= 0.0 ||
      InpMaxCapitalUsePercent <= 0.0 || InpMaxCapitalUsePercent > 100.0 ||
      InpPreventiveLossPercent <= 0.0 ||
      InpSuspendLossPercent <= InpPreventiveLossPercent ||
      InpATRPeriod < 2 || InpATRStopMultiplier <= 0.0 ||
      InpBreakoutPeriod < 2 || InpVolumeAveragePeriod < 2 ||
      InpRelativeStrengthPeriod < 2 || InpExitLowPeriod < 2 ||
      InpBenchmarkSymbol == "" || InpFeeRatePerSide < 0.0 ||
      InpFixedFeePerSideBRL < 0.0 || InpStopSlippageTicks < 0)
      return INIT_PARAMETERS_INCORRECT;

   if(!B3TesterReady(InpStartingCapitalBRL, InpBenchmarkSymbol))
      return INIT_FAILED;

   g_atrHandle = iATR(_Symbol, PERIOD_D1, InpATRPeriod);
   if(g_atrHandle == INVALID_HANDLE)
      return INIT_FAILED;
   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(g_atrHandle != INVALID_HANDLE)
      IndicatorRelease(g_atrHandle);
}

void OnTick()
{
   if(!MQLInfoInteger(MQL_TESTER))
      return;

   const bool entriesAllowed = B3ManageLossLimits(g_trade, InpMagicNumber,
                                                   InpStartingCapitalBRL,
                                                   InpPreventiveLossPercent,
                                                   InpSuspendLossPercent,
                                                   g_suspended);
   if(g_suspended)
      return;

   if(!B3NewDailyBar(g_lastBarTime))
      return;

   const int requiredBars = MathMax(MathMax(InpBreakoutPeriod,
                                            InpVolumeAveragePeriod),
                                    MathMax(InpRelativeStrengthPeriod,
                                            InpExitLowPeriod)) + 2;
   MqlRates rates[];
   if(!B3ReadRates(requiredBars, rates))
      return;

   double atr = 0.0;
   if(B3OwnPosition(InpMagicNumber))
   {
      if(GetATR(atr))
         ManageOpenPosition(rates, atr);
      return;
   }

   if(!entriesAllowed)
      return;

   if(!BreakoutSignal(rates, atr))
      return;

   B3PlaceLong(g_trade, InpMagicNumber, InpStartingCapitalBRL,
               InpRiskPerTradeBRL, InpMaxCapitalUsePercent,
               InpFeeRatePerSide, InpFixedFeePerSideBRL,
               InpStopSlippageTicks, atr, InpATRStopMultiplier);
}
