#property strict
#property version   "1.00"
#property description "Reversao na banda inferior de canal ascendente; Strategy Tester only."

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
input int    InpRegressionPeriod            = 120;
input int    InpFastMAPeriod                = 50;
input int    InpSlowMAPeriod                = 200;
input double InpLowerChannelZonePercent     = 30.0;
input long   InpMagicNumber                 = 8101201;

int      g_atrHandle = INVALID_HANDLE;
datetime g_lastBarTime = 0;
bool     g_suspended = false;
CTrade   g_trade;

double MeanClose(const MqlRates &rates[], const int firstShift, const int count)
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

bool LowerChannelTouched(const MqlRates &bar,
                         const double intercept,
                         const double slope,
                         const double sigma,
                         const int x)
{
   const double center = intercept + slope * x;
   const double lower = MathExp(center - 2.0 * sigma);
   const double lowerZoneSigma = 2.0 - 4.0 * InpLowerChannelZonePercent / 100.0;
   const double lowerZone = MathExp(center - lowerZoneSigma * sigma);
   return bar.low <= lowerZone && bar.high >= lower && bar.close >= lower;
}

bool UptrendPullbackSignal(MqlRates &rates[], double &atr)
{
   if(!GetATR(atr))
      return false;

   double closes[];
   ArrayResize(closes, InpRegressionPeriod);
   double meanY = 0.0;
   for(int i = 0; i < InpRegressionPeriod; ++i)
   {
      const int shift = InpRegressionPeriod - i;
      if(rates[shift].close <= 0.0)
         return false;
      closes[i] = MathLog(rates[shift].close);
      meanY += closes[i];
   }
   meanY /= InpRegressionPeriod;

   const double meanX = (InpRegressionPeriod - 1.0) / 2.0;
   double covariance = 0.0;
   double varianceX = 0.0;
   for(int i = 0; i < InpRegressionPeriod; ++i)
   {
      covariance += (i - meanX) * (closes[i] - meanY);
      varianceX += (i - meanX) * (i - meanX);
   }
   if(varianceX <= 0.0)
      return false;

   const double slope = covariance / varianceX;
   const double intercept = meanY - slope * meanX;
   double residualSum = 0.0;
   for(int i = 0; i < InpRegressionPeriod; ++i)
   {
      const double residual = closes[i] - intercept - slope * i;
      residualSum += residual * residual;
   }
   const double sigma = MathSqrt(residualSum / (InpRegressionPeriod - 2.0));
   if(slope <= 0.0 || sigma <= 1e-12)
      return false;

   const double maFast = MeanClose(rates, 1, InpFastMAPeriod);
   const double maFast20SessionsAgo = MeanClose(rates, 21, InpFastMAPeriod);
   const double maSlow = MeanClose(rates, 1, InpSlowMAPeriod);
   const double lowerNow = MathExp(intercept + slope * (InpRegressionPeriod - 1) -
                                   2.0 * sigma);
   const bool touched = LowerChannelTouched(rates[1], intercept, slope, sigma,
                                             InpRegressionPeriod - 1) ||
                        LowerChannelTouched(rates[2], intercept, slope, sigma,
                                             InpRegressionPeriod - 2);

   return rates[1].close > maSlow &&
          maFast > maFast20SessionsAgo &&
          maFast > maSlow &&
          touched &&
          rates[1].close > rates[2].high &&
          rates[1].close >= lowerNow;
}

void ManageOpenPosition(MqlRates &rates[], const double atr)
{
   if(!B3OwnPosition(InpMagicNumber))
      return;

   const double maFast = MeanClose(rates, 1, InpFastMAPeriod);
   const double maSlow = MeanClose(rates, 1, InpSlowMAPeriod);
   const double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   const double entryPrice = PositionGetDouble(POSITION_PRICE_OPEN);
   const int entryShift = iBarShift(_Symbol, PERIOD_D1,
                                    (datetime)PositionGetInteger(POSITION_TIME), false);

   double meanY = 0.0;
   double y[];
   ArrayResize(y, InpRegressionPeriod);
   for(int i = 0; i < InpRegressionPeriod; ++i)
   {
      y[i] = MathLog(rates[InpRegressionPeriod - i].close);
      meanY += y[i];
   }
   meanY /= InpRegressionPeriod;
   const double meanX = (InpRegressionPeriod - 1.0) / 2.0;
   double covariance = 0.0;
   double varianceX = 0.0;
   for(int i = 0; i < InpRegressionPeriod; ++i)
   {
      covariance += (i - meanX) * (y[i] - meanY);
      varianceX += (i - meanX) * (i - meanX);
   }
   const double slope = (varianceX > 0.0 ? covariance / varianceX : 0.0);
   const bool trendLost = slope <= 0.0 || rates[1].close < maSlow || maFast < maSlow;
   if(trendLost)
   {
      if(!g_trade.PositionClose(_Symbol))
         PrintFormat("Falha ao fechar por perda de tendencia: %u", g_trade.ResultRetcode());
      return;
   }

   if(atr <= 0.0 || entryShift < 1 || bid <= entryPrice)
      return;

   const int highestShift = iHighest(_Symbol, PERIOD_D1, MODE_HIGH, entryShift, 1);
   if(highestShift < 0)
      return;
   const double highestSinceEntry = MathMax(entryPrice,
                                            iHigh(_Symbol, PERIOD_D1, highestShift));

   B3RaiseStop(g_trade, highestSinceEntry - atr * InpATRStopMultiplier);
}

int OnInit()
{
   if(InpStartingCapitalBRL <= 0.0 || InpRiskPerTradeBRL <= 0.0 ||
      InpMaxCapitalUsePercent <= 0.0 || InpMaxCapitalUsePercent > 100.0 ||
      InpPreventiveLossPercent <= 0.0 ||
      InpSuspendLossPercent <= InpPreventiveLossPercent ||
      InpATRPeriod < 2 || InpATRStopMultiplier <= 0.0 ||
      InpRegressionPeriod <= 2 || InpFastMAPeriod < 2 ||
      InpSlowMAPeriod <= InpFastMAPeriod ||
      InpLowerChannelZonePercent < 0.0 || InpLowerChannelZonePercent > 100.0 ||
      InpFeeRatePerSide < 0.0 || InpFixedFeePerSideBRL < 0.0 ||
      InpStopSlippageTicks < 0)
      return INIT_PARAMETERS_INCORRECT;

   if(!B3TesterReady(InpStartingCapitalBRL, ""))
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

   MqlRates rates[];
   const int requiredBars = MathMax(InpSlowMAPeriod, InpRegressionPeriod) + 2;
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

   if(!UptrendPullbackSignal(rates, atr))
      return;

   B3PlaceLong(g_trade, InpMagicNumber, InpStartingCapitalBRL,
               InpRiskPerTradeBRL, InpMaxCapitalUsePercent,
               InpFeeRatePerSide, InpFixedFeePerSideBRL,
               InpStopSlippageTicks, atr, InpATRStopMultiplier);
}
