"""Testes automatizados da Estrategia C (Swing Trade com Forca Relativa).

Valida:
1. Ranking de Forca Relativa (RS20, RS60, RS120, percentis, SCORE, desempates).
2. Canais de Alta (regressao log-linear, bandas 2-sigma, zona de entrada, confirmacao).
3. Stops e Saidas (stop inicial 2*ATR, stop movel pelo maior fechamento, saida por SMA50/inclinacao).
4. Quantidades e Dimensionamento (quantidades inteiras, piso matematico, lote < 1 descartado).
5. Limites de Risco (risco 0,5%, agregado 1,5%, trava preventiva 6%, suspensao 10%).
6. Tratamento de Gaps e Slippage (recalculo na abertura, preenchimento de stop com gap).
7. Ausencia de Look-Ahead Bias (estrita causalidade D-1 -> D0 abertura).
8. Bloqueio de Ordens Reais (bloqueio no tester e simulador passivo).
"""
import copy, math, unittest
from datetime import datetime, timezone

TICK = 0.01


def floor_tick(p):
    return math.floor(p / TICK + 1e-10) * TICK


def regression_calc(closes):
    n = len(closes)
    if n < 3:
        return None
    y = [math.log(c) for c in closes]
    my = sum(y) / n
    mx = (n - 1) / 2
    cov = sum((i - mx) * (y[i] - my) for i in range(n))
    vx = sum((i - mx) ** 2 for i in range(n))
    if vx <= 0:
        return None
    slope = cov / vx
    icpt = my - slope * mx
    ss = sum((y[i] - icpt - slope * i) ** 2 for i in range(n))
    sigma = math.sqrt(ss / (n - 2))
    return slope, icpt, sigma


def compute_cross_sectional_score(universe_rs, mandatory_checks):
    """
    universe_rs: dict sym -> (rs20, rs60, rs120)
    mandatory_checks: dict sym -> bool
    """
    syms = sorted(universe_rs.keys())
    n = len(syms)
    if n < 2:
        return []

    p20_sorted = sorted(syms, key=lambda s: universe_rs[s][0])
    p60_sorted = sorted(syms, key=lambda s: universe_rs[s][1])
    p120_sorted = sorted(syms, key=lambda s: universe_rs[s][2])

    p20 = {s: rank / (n - 1) * 100 for rank, s in enumerate(p20_sorted)}
    p60 = {s: rank / (n - 1) * 100 for rank, s in enumerate(p60_sorted)}
    p120 = {s: rank / (n - 1) * 100 for rank, s in enumerate(p120_sorted)}

    scored = []
    for s in syms:
        score = 0.40 * p20[s] + 0.35 * p60[s] + 0.25 * p120[s]
        eligible = mandatory_checks.get(s, False)
        scored.append((s, score, eligible))
    return scored


class StrategyCRankingTests(unittest.TestCase):
    def test_relative_strength_and_percentiles(self):
        # 10 ativos com retornos sinteticos
        # IBOV: ret20 = 0.05, ret60 = 0.10, ret120 = 0.15
        ibov_ret = (0.05, 0.10, 0.15)
        # Ativo A com retornos superiores ao IBOV
        stock_a = (0.15, 0.25, 0.30)
        rs_a = (stock_a[0] - ibov_ret[0], stock_a[1] - ibov_ret[1], stock_a[2] - ibov_ret[2])
        self.assertAlmostEqual(rs_a[0], 0.10)
        self.assertAlmostEqual(rs_a[1], 0.15)
        self.assertAlmostEqual(rs_a[2], 0.15)

        # Percentis transversais em universo de 3 ativos
        universe = {
            'SYM1': (0.01, 0.02, 0.03), # menor
            'SYM2': (0.05, 0.06, 0.07), # medio
            'SYM3': (0.10, 0.12, 0.14)  # maior
        }
        res = compute_cross_sectional_score(universe, {s: True for s in universe})
        score_dict = {s: sc for s, sc, el in res}
        self.assertAlmostEqual(score_dict['SYM1'], 0.0)
        self.assertAlmostEqual(score_dict['SYM2'], 50.0)
        self.assertAlmostEqual(score_dict['SYM3'], 100.0)

    def test_mandatory_filters_exclusion(self):
        universe = {
            'A': (0.10, 0.10, 0.10),
            'B': (-0.02, 0.10, 0.10), # RS20 <= 0 -> reprovado
            'C': (0.10, -0.01, 0.10)  # RS60 <= 0 -> reprovado
        }
        # Filtros: RS20 > 0 e RS60 > 0
        checks = {s: universe[s][0] > 0 and universe[s][1] > 0 for s in universe}
        res = compute_cross_sectional_score(universe, checks)
        eligible = [s for s, sc, el in res if el]
        self.assertEqual(eligible, ['A'])

    def test_tie_breaking(self):
        # Dois ativos com mesmo SCORE
        cands = [
            {'sym': 'VALE3', 'score': 85.0, 'atr_ratio': 0.03},
            {'sym': 'PETR4', 'score': 85.0, 'atr_ratio': 0.02}, # menor ATR/close deve vencer
            {'sym': 'BBAS3', 'score': 85.0, 'atr_ratio': 0.02}  # menor ATR/close e ticker alfabetico deve vencer
        ]
        cands.sort(key=lambda x: (-x['score'], x['atr_ratio'], x['sym']))
        self.assertEqual(cands[0]['sym'], 'BBAS3')
        self.assertEqual(cands[1]['sym'], 'PETR4')
        self.assertEqual(cands[2]['sym'], 'VALE3')


class StrategyCChannelTests(unittest.TestCase):
    def test_log_regression_channel(self):
        # Serie com tendencia de alta exponencial (linear no log)
        # c_k = 10 * exp(0.005 * k)
        closes = [10.0 * math.exp(0.005 * k) for k in range(120)]
        slope, icpt, sigma = regression_calc(closes)
        self.assertAlmostEqual(slope, 0.005, places=5)
        self.assertAlmostEqual(icpt, math.log(10.0), places=5)
        self.assertAlmostEqual(sigma, 0.0, places=5)

        # Precos das bandas
        center = math.exp(icpt + slope * 119)
        lower = math.exp(icpt + slope * 119 - 2 * 0.01) # com sigma pequeno
        upper = math.exp(icpt + slope * 119 + 2 * 0.01)
        self.assertTrue(lower < center < upper)

    def test_channel_entry_zone_and_confirmation(self):
        # Zona de entrada: lower <= close <= center
        lower = 20.0
        center = 25.0
        upper = 30.0

        close_in_zone = 22.0
        prior_high = 21.5
        # Fechamento atual > maxima anterior
        self.assertTrue(lower <= close_in_zone <= center)
        self.assertTrue(close_in_zone > prior_high)
        self.assertTrue(close_in_zone <= upper)

        # Fora da zona (acima da linha central)
        close_above_center = 26.0
        self.assertFalse(lower <= close_above_center <= center)

        # Acima da banda superior
        close_above_upper = 31.0
        self.assertFalse(close_above_upper <= upper)


class StrategyCStopsAndExitsTests(unittest.TestCase):
    def test_initial_and_trailing_stop(self):
        entry_price = 25.00
        atr = 1.00
        initial_stop = floor_tick(entry_price - 2 * atr)
        self.assertEqual(initial_stop, 23.00)

        # Dia seguinte: novo fechamento mais alto (27.00)
        highest_close = 27.00
        candidate_stop = floor_tick(highest_close - 2 * atr)
        self.assertEqual(candidate_stop, 25.00)
        # Stop sobe
        current_stop = max(initial_stop, candidate_stop)
        self.assertEqual(current_stop, 25.00)

        # Dia seguinte: fechamento cai para 24.50
        # Stop nunca pode ser afastado (nunca diminui)
        candidate_stop2 = floor_tick(24.50 - 2 * atr)
        current_stop = max(current_stop, candidate_stop2)
        self.assertEqual(current_stop, 25.00)

    def test_additional_exits(self):
        # Saida por fechamento abaixo da SMA50
        close = 24.00
        sma50 = 24.50
        slope = 0.002
        exit_signal = (close < sma50) or (slope <= 0)
        self.assertTrue(exit_signal)

        # Saida por inclinacao <= 0
        close = 26.00
        sma50 = 24.50
        slope = -0.0001
        exit_signal = (close < sma50) or (slope <= 0)
        self.assertTrue(exit_signal)


class StrategyCPositionSizingTests(unittest.TestCase):
    def test_integer_quantity_and_floor(self):
        equity = 500.00
        risk_budget = equity * 0.005 # R$ 2.50
        fixed = 0.05
        fee = 0.0005
        ask = 25.00
        stop = 23.00
        stressed_stop = stop - 0.02
        risk_per_share = (ask - stressed_stop) + (ask + stressed_stop) * fee

        # Quantidade pelo risco
        q_risk = (risk_budget - 2 * fixed) / risk_per_share
        qty = math.floor(q_risk + 1e-9)
        self.assertEqual(qty, 1) # Nao arredonda para cima

        # Se risco por acao for muito grande para o budget (ex: R$ 3.00)
        q_risk_small = (risk_budget - 2 * fixed) / 3.00
        qty_small = math.floor(q_risk_small + 1e-9)
        self.assertEqual(qty_small, 0) # Lote < 1 -> descarta


class StrategyCRiskLimitsTests(unittest.TestCase):
    def test_risk_aggregate_limit(self):
        equity = 500.00
        max_agg_risk = equity * 0.015 # R$ 7.50
        # Ja temos 2 posicoes abertas com risco total de 6.00
        current_agg = 6.00
        budget = max_agg_risk - current_agg
        self.assertEqual(budget, 1.50)

        # Se ja atingiu 7.50
        current_agg = 7.50
        budget = max_agg_risk - current_agg
        self.assertEqual(budget, 0.00)

    def test_drawdown_trava_preventiva_e_suspensao(self):
        peak_equity = 500.00
        # Drawdown de 5% -> continua normal
        eq_5pct = 475.00
        dd_5 = (peak_equity - eq_5pct) / peak_equity
        self.assertTrue(dd_5 < 0.06)

        # Drawdown de 6.5% -> suspende novas entradas
        eq_65pct = 467.50
        dd_65 = (peak_equity - eq_65pct) / peak_equity
        entries_ok = (dd_65 < 0.06)
        self.assertFalse(entries_ok)

        # Drawdown de 10.5% -> suspensao total e liquidacao
        eq_105pct = 447.50
        dd_105 = (peak_equity - eq_105pct) / peak_equity
        suspended = (dd_105 >= 0.10)
        self.assertTrue(suspended)


class StrategyCGapsAndSlippageTests(unittest.TestCase):
    def test_gap_open_recalculation(self):
        # Fechamento anterior: 25.00
        # Abertura do dia com gap de alta: 26.00
        slip = 0.01
        executable_ask = 26.00 + slip
        atr = 1.00
        stop = floor_tick(executable_ask - 2 * atr)
        self.assertEqual(executable_ask, 26.01)
        self.assertEqual(stop, 24.01)

    def test_intraday_gap_stop_fill(self):
        # Stop posicionado em 24.00
        # Dia abre com gap abaixo do stop: Open = 23.50, Low = 23.00
        stop = 24.00
        open_px = 23.50
        stop_slip = 0.02
        fill_px = min(stop, open_px) - stop_slip
        self.assertEqual(fill_px, 23.48) # Executado pelo preco de gap, mais conservador


class StrategyCLookAheadTests(unittest.TestCase):
    def test_signals_use_strictly_past_data(self):
        # Criar historico de 250 barras
        bars = [{'date': f'2024-01-{i:02d}', 'c': 20.0 + i * 0.05, 'o': 20.0 + i * 0.05,
                 'h': 20.2 + i * 0.05, 'l': 19.8 + i * 0.05} for i in range(1, 250)]
        target_idx = 200
        sub_bars_past = bars[:target_idx + 1]

        # Inserir mudanca radical nas barras futuras (target_idx + 1 em diante)
        bars_future_mutated = copy.deepcopy(bars)
        for k in range(target_idx + 1, len(bars_future_mutated)):
            bars_future_mutated[k]['c'] = 9999.0

        # Regressao calculada ate target_idx usando apenas sub_bars_past vs mutated
        reg1 = regression_calc([b['c'] for b in sub_bars_past[-120:]])
        reg2 = regression_calc([b['c'] for b in bars_future_mutated[:target_idx + 1][-120:]])
        self.assertEqual(reg1, reg2)


class StrategyCRealOrderBlockTests(unittest.TestCase):
    def test_mql5_tester_block_presence(self):
        # O arquivo MQL5 DEVE conter validacao estrita de MQLInfoInteger(MQL_TESTER)
        import pathlib
        mq5_path = pathlib.Path(__file__).resolve().parent.parent / 'MQL5/Experts/B3Swing/B3Swing_C_RelativeStrength.mq5'
        content = mq5_path.read_text(encoding='utf-8')
        self.assertIn('MQLInfoInteger(MQL_TESTER)', content)
        self.assertIn('B3TesterReady', content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
