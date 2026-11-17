#ifndef B3_SWING_COMMON_MQH
#define B3_SWING_COMMON_MQH

#include <Trade/Trade.mqh>

bool B3TesterReady(const double startingCapital, const string benchmarkSymbol)
{
   if(!MQLInfoInteger(MQL_TESTER))
   {
      Print("Execucao bloqueada: estes EAs funcionam somente no Strategy Tester.");
      return false;
   }

   if(MathAbs(AccountInfoDouble(ACCOUNT_BALANCE) - startingCapital) > 0.01)
   {
      PrintFormat("Saldo inicial do Tester deve ser %.2f BRL.", startingCapital);
      return false;
   }

   if(AccountInfoString(ACCOUNT_CURRENCY) != "BRL")
   {
      Print("Execucao bloqueada: a moeda da conta do Tester deve ser BRL.");
      return false;
   }

   const double minVolume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   const double contractSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
   if(minVolume <= 0.0 || contractSize <= 0.0 || minVolume * contractSize > 1.0 + 1e-8)
   {
      Print("Simbolo nao habilita lote fracionario de ate uma acao por volume minimo.");
      return false;
   }

   if(benchmarkSymbol != "" && !SymbolSelect(benchmarkSymbol, true))
   {
      PrintFormat("Nao foi possivel selecionar o benchmark %s.", benchmarkSymbol);
      return false;
   }

   return true;
}

bool B3NewDailyBar(datetime &lastBarTime)
{
   const datetime currentBarTime = iTime(_Symbol, PERIOD_D1, 0);
   if(currentBarTime <= 0 || currentBarTime == lastBarTime)
      return false;

   lastBarTime = currentBarTime;
   return true;
}

bool B3ReadRates(const int count, MqlRates &rates[])
{
   ArraySetAsSeries(rates, true);
   return CopyRates(_Symbol, PERIOD_D1, 0, count, rates) == count;
}

double B3RateVolume(const MqlRates &bar)
{
   return (bar.real_volume > 0 ? (double)bar.real_volume : (double)bar.tick_volume);
}

double B3RoundDownToTick(const double price)
{
   const double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tickSize <= 0.0)
      return 0.0;
   return NormalizeDouble(MathFloor(price / tickSize + 1e-10) * tickSize, _Digits);
}

bool B3OwnPosition(const long magic)
{
   if(!PositionSelect(_Symbol))
      return false;
   return PositionGetInteger(POSITION_MAGIC) == magic;
}

bool B3ManageLossLimits(CTrade &trade,
                        const long magic,
                        const double startingCapital,
                        const double preventiveLossPercent,
                        const double suspendLossPercent,
                        bool &suspended)
{
   if(!MQLInfoInteger(MQL_TESTER))
      return false;

   const double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity <= startingCapital * (1.0 - suspendLossPercent / 100.0))
   {
      suspended = true;
      if(B3OwnPosition(magic) && !trade.PositionClose(_Symbol))
         PrintFormat("Falha ao fechar posicao no limite de suspensao: %u",
                     trade.ResultRetcode());
      return false;
   }

   if(suspended || equity <= startingCapital * (1.0 - preventiveLossPercent / 100.0))
      return false;

   return true;
}

bool B3CalculateVolume(const double entryPrice,
                       const double stopPrice,
                       const double startingCapital,
                       const double riskPerTrade,
                       const double maxCapitalPercent,
                       const double feeRatePerSide,
                       const double fixedFeePerSide,
                       const int stopSlippageTicks,
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

   const double stressedStop = MathMax(tickSize,
                                       stopPrice - stopSlippageTicks * tickSize);
   double grossLossForOneVolume = 0.0;
   if(!OrderCalcProfit(ORDER_TYPE_BUY, _Symbol, 1.0, entryPrice, stressedStop,
                       grossLossForOneVolume) || grossLossForOneVolume >= 0.0)
      return false;

   const double variableFeesForOneVolume =
      (entryPrice + stressedStop) * contractSize * feeRatePerSide;
   const double fixedFees = 2.0 * fixedFeePerSide;
   const double riskBudget = MathMin(riskPerTrade,
                                     MathMax(0.0, AccountInfoDouble(ACCOUNT_EQUITY)));
   const double riskPerVolume = -grossLossForOneVolume + variableFeesForOneVolume;
   if(riskBudget <= fixedFees || riskPerVolume <= 0.0)
      return false;

   const double capitalBase = MathMin(startingCapital,
                                      AccountInfoDouble(ACCOUNT_EQUITY));
   const double maxNotional = capitalBase * maxCapitalPercent / 100.0;
   const double notionalPerVolume = entryPrice * contractSize;
   if(maxNotional <= 0.0 || notionalPerVolume <= 0.0)
      return false;

   const double riskLimitedVolume = (riskBudget - fixedFees) / riskPerVolume;
   const double capitalLimitedVolume = maxNotional / notionalPerVolume;
   const double rawVolume = MathMin(MathMin(riskLimitedVolume, capitalLimitedVolume),
                                    maxVolume);
   volume = MathFloor(rawVolume / volumeStep + 1e-10) * volumeStep;
   volume = NormalizeDouble(volume, 8);
   if(volume < minVolume)
      return false;

   const double modeledRisk = volume * riskPerVolume + fixedFees;
   const double modeledNotional = volume * notionalPerVolume;
   return modeledRisk <= riskBudget + 1e-7 &&
          modeledNotional <= maxNotional + 1e-7;
}

bool B3PlaceLong(CTrade &trade,
                 const long magic,
                 const double startingCapital,
                 const double riskPerTrade,
                 const double maxCapitalPercent,
                 const double feeRatePerSide,
                 const double fixedFeePerSide,
                 const int stopSlippageTicks,
                 const double atr,
                 const double atrStopMultiplier)
{
   if(!MQLInfoInteger(MQL_TESTER) || PositionsTotal() > 0 ||
      atr <= 0.0 || atrStopMultiplier <= 0.0)
      return false;

   const double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   const double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(ask <= 0.0 || tickSize <= 0.0)
      return false;

   const double stop = B3RoundDownToTick(ask - atr * atrStopMultiplier);
   double volume = 0.0;
   if(stop <= 0.0 ||
      !B3CalculateVolume(ask, stop, startingCapital, riskPerTrade,
                         maxCapitalPercent, feeRatePerSide, fixedFeePerSide,
                         stopSlippageTicks, volume))
   {
      Print("Entrada descartada: lote minimo excede risco/capital disponivel.");
      return false;
   }

   trade.SetExpertMagicNumber(magic);
   trade.SetTypeFillingBySymbol(_Symbol);
   if(!trade.Buy(volume, _Symbol, 0.0, stop, 0.0, "B3 swing tester only"))
   {
      PrintFormat("Ordem de compra rejeitada no Tester: %u", trade.ResultRetcode());
      return false;
   }
   return true;
}

bool B3RaiseStop(CTrade &trade, const double candidateStop)
{
   if(!MQLInfoInteger(MQL_TESTER) || !PositionSelect(_Symbol))
      return false;

   const double currentStop = PositionGetDouble(POSITION_SL);
   const double candidate = B3RoundDownToTick(candidateStop);
   if(candidate <= 0.0 || (currentStop > 0.0 && candidate <= currentStop))
      return false;

   if(!trade.PositionModify(_Symbol, candidate, 0.0))
   {
      PrintFormat("Falha ao mover stop no Tester: %u", trade.ResultRetcode());
      return false;
   }
   return true;
}

#endif
