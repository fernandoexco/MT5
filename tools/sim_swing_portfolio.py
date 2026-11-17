"""Simulador consolidado das estrategias A e B (porta da logica dos EAs MQL5).

Nao envia ordens. Le D1 coletado do MT5 (reports/mt5run/data) e simula carteira
com caixa compartilhado, quantidades inteiras, ate N posicoes e travas de drawdown.
Uso: py -3.13 tools/sim_swing_portfolio.py  -> reports/mt5run/results.json
"""
import json, math, pathlib, random, statistics, itertools
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'reports/mt5run/data'
UNIVERSE = "ITUB4 BBAS3 WEGE3 GGBR4 PETR4 VALE3 BBDC4 ABEV3 EGIE3 SUZB3".split()
TICK = 0.01
END = '2026-11-16'
PERIODS = {'desenvolvimento(2021-11..2023)': ('2021-11-16', '2023-12-31'),
           'validacao(2024)': ('2024-01-01', '2024-12-31'),
           'fora_da_amostra(2025..2026-11-16)': ('2025-01-01', END)}


def load(sym):
    h = json.load(open(DATA / f'{sym}.json', encoding='utf-8'))['history']
    return [dict(date=r['time'][:10], o=r['open'], h=r['high'], l=r['low'], c=r['close'],
                 v=float(r.get('volume') or r.get('tick_volume') or 0)) for r in h]


BARS = {s: load(s) for s in UNIVERSE + ['IBOV', 'BOVA11']}
IDX = {s: {b['date']: i for i, b in enumerate(BARS[s])} for s in BARS}
DATES = sorted({b['date'] for s in UNIVERSE for b in BARS[s]})


def atr14(bars, i, n=14):
    """ATR(Wilder) calculada ate a barra i (fechada), como iATR do MT5."""
    if i < n:
        return None
    trs = []
    for k in range(1, i + 1):
        b, p = bars[k], bars[k - 1]
        trs.append(max(b['h'] - b['l'], abs(b['h'] - p['c']), abs(b['l'] - p['c'])))
    a = sum(trs[:n]) / n
    for t in trs[n:]:
        a = (a * (n - 1) + t) / n
    return a


class Series:
    """Pre-calcula ATR para cada simbolo (O(n))."""
    def __init__(self, bars, n=14):
        self.atr = [None] * len(bars)
        trs = [None]
        for k in range(1, len(bars)):
            b, p = bars[k], bars[k - 1]
            trs.append(max(b['h'] - b['l'], abs(b['h'] - p['c']), abs(b['l'] - p['c'])))
        if len(bars) > n:
            a = sum(trs[1:n + 1]) / n
            self.atr[n] = a
            for k in range(n + 1, len(bars)):
                a = (a * (n - 1) + trs[k]) / n
                self.atr[k] = a


def sma(bars, end, n):
    """Media dos n fechamentos terminando em end (inclusive)."""
    if end - n + 1 < 0:
        return None
    return sum(b['c'] for b in bars[end - n + 1:end + 1]) / n


def regression(bars, end, n):
    """Regressao linear de ln(close) nas n barras terminando em end."""
    if end - n + 1 < 0:
        return None
    y = [math.log(b['c']) for b in bars[end - n + 1:end + 1]]
    my = sum(y) / n
    mx = (n - 1) / 2
    cov = sum((i - mx) * (y[i] - my) for i in range(n))
    vx = sum((i - mx) ** 2 for i in range(n))
    slope = cov / vx
    icpt = my - slope * mx
    ss = sum((y[i] - icpt - slope * i) ** 2 for i in range(n))
    sigma = math.sqrt(ss / (n - 2))
    return slope, icpt, sigma


def floor_tick(p):
    return math.floor(p / TICK + 1e-10) * TICK


def default_params():
    return dict(capital=500.0, risk=2.5, max_cap_pct=90.0, prev=6.0, susp=10.0,
                fee=0.0005, fixed=0.05, stop_slip_ticks=2, entry_slip_ticks=1,
                atr_mult=2.0, reg=120, fast=50, slow=200, zone=30.0,
                brk=20, volavg=20, rs=60, exitlow=10, max_pos=3, max_agg_risk=7.5,
                cost_mult=1.0, slip_mult=1.0)


def sig_A(bars, sa, i, p):
    """Sinal A avaliado com barra i = shift1 (ultima fechada)."""
    need = max(p['slow'], p['reg']) + 2
    if i < need or sa.atr[i] is None:
        return None
    reg = regression(bars, i, p['reg'])
    slope, icpt, sigma = reg
    if slope <= 0 or sigma <= 1e-12:
        return None
    maF, maF20, maS = sma(bars, i, p['fast']), sma(bars, i - 20, p['fast']), sma(bars, i, p['slow'])
    n = p['reg']
    lower_now = math.exp(icpt + slope * (n - 1) - 2 * sigma)
    zs = 2.0 - 4.0 * p['zone'] / 100.0

    def touched(k, x):
        c = icpt + slope * x
        lo = math.exp(c - 2 * sigma)
        lz = math.exp(c - zs * sigma)
        b = bars[k]
        return b['l'] <= lz and b['h'] >= lo and b['c'] >= lo
    t = touched(i, n - 1) or touched(i - 1, n - 2)
    ok = (bars[i]['c'] > maS and maF > maF20 and maF > maS and t
          and bars[i]['c'] > bars[i - 1]['h'] and bars[i]['c'] >= lower_now)
    return sa.atr[i] if ok else None


def sig_B(bars, sa, i, p, ibars, iidx):
    need = max(p['brk'], p['volavg'], p['rs'], p['exitlow']) + 2
    if i < need or sa.atr[i] is None:
        return None
    prior_high = max(b['h'] for b in bars[i - p['brk']:i])           # shifts 2..brk+1
    avg_vol = sum(b['v'] for b in bars[i - p['volavg']:i]) / p['volavg']
    if avg_vol <= 0 or bars[i]['v'] <= avg_vol or bars[i]['c'] <= prior_high:
        return None
    j = iidx.get(bars[i]['date'])
    if j is None or j - p['rs'] < 0:
        return None
    s_ret = bars[i]['c'] / bars[i - p['rs']]['c'] - 1
    b_ret = ibars[j]['c'] / ibars[j - p['rs']]['c'] - 1
    return sa.atr[i] if s_ret > b_ret else None


def exit_signal_A(bars, i, p):
    maF, maS = sma(bars, i, p['fast']), sma(bars, i, p['slow'])
    reg = regression(bars, i, p['reg'])
    slope = reg[0] if reg else 0
    return slope <= 0 or bars[i]['c'] < maS or maF < maS


def trail_A(bars, sa, i, entry_i, entry_px, bid, p):
    if sa.atr[i] is None or bid <= entry_px:
        return None
    hi = max(entry_px, max(b['h'] for b in bars[max(entry_i, 0):i + 1]) if i >= entry_i else entry_px)
    return hi - sa.atr[i] * p['atr_mult']


def exit_signal_B(bars, i, p):
    low = min(b['l'] for b in bars[i - p['exitlow']:i])             # shifts 2..exitlow+1
    return bars[i]['c'] < low, low


def run(strategy, p, universe=None, start=None, end=END):
    universe = universe or UNIVERSE
    SER = {s: Series(BARS[s]) for s in universe}
    ib, iidx = BARS['IBOV'], IDX['IBOV']
    cash = p['capital']
    pos = {}                 # sym -> dict
    trades, equity = [], []
    suspended = False
    slip = p['stop_slip_ticks'] * TICK * p['slip_mult']
    eslip = p['entry_slip_ticks'] * TICK * p['slip_mult']
    fee = p['fee'] * p['cost_mult']
    fixed = p['fixed'] * p['cost_mult']
    for d in DATES:
        if d > end:
            break
        # --- abertura: gestao de posicoes abertas (dados ate t-1) ---
        for s in list(pos):
            bars = BARS[s]
            t = IDX[s].get(d)
            if t is None:
                continue
            i = t - 1
            ps = pos[s]
            op = bars[t]['o']
            close_now = False
            if strategy == 'A':
                close_now = exit_signal_A(bars, i, p)
                if not close_now:
                    new = trail_A(bars, SER[s], i, ps['entry_i'], ps['entry'], op, p)
                    if new is not None:
                        new = floor_tick(new)
                        if new > ps['stop']:
                            ps['stop'] = new
            else:
                close_now, low10 = exit_signal_B(bars, i, p)
                if not close_now and SER[s].atr[i] and op > ps['entry']:
                    new = floor_tick(max(low10, op - SER[s].atr[i] * p['atr_mult']))
                    if new > ps['stop']:
                        ps['stop'] = new
            if close_now:
                px = op - eslip
                cash += _close(ps, px, d, 'sinal', fee, fixed, trades)
                del pos[s]
        # --- trava por drawdown (equity ao abrir, marcada na abertura) ---
        eq_open = cash + sum(ps['qty'] * (BARS[s][IDX[s][d]]['o'] if d in IDX[s] else ps['last'])
                             for s, ps in pos.items())
        if eq_open <= p['capital'] * (1 - p['susp'] / 100):
            suspended = True
            for s in list(pos):
                t = IDX[s].get(d)
                px = (BARS[s][t]['o'] - eslip) if t is not None else pos[s]['last']
                cash += _close(pos[s], px, d, 'suspensao', fee, fixed, trades)
                del pos[s]
        entries_ok = (not suspended) and eq_open > p['capital'] * (1 - p['prev'] / 100)
        # --- entradas (sinal em t-1, execucao na abertura de t) ---
        if entries_ok:
            for s in universe:
                if s in pos or len(pos) >= p['max_pos']:
                    continue
                t = IDX[s].get(d)
                if t is None or t < 1:
                    continue
                i = t - 1
                bars = BARS[s]
                atr = (sig_A(bars, SER[s], i, p) if strategy == 'A'
                       else sig_B(bars, SER[s], i, p, ib, iidx))
                if not atr:
                    continue
                ask = bars[t]['o'] + eslip
                stop = floor_tick(ask - atr * p['atr_mult'])
                if stop <= 0 or stop >= ask:
                    continue
                stressed = max(TICK, stop - p['stop_slip_ticks'] * TICK * p['slip_mult'])
                risk_ps = (ask - stressed) + (ask + stressed) * fee
                agg = sum(q['risk'] for q in pos.values())
                budget = min(p['risk'], max(0.0, eq_open), p['max_agg_risk'] - agg)
                if budget <= 2 * fixed or risk_ps <= 0:
                    continue
                cap_room = min(cash, p['capital'] * p['max_cap_pct'] / 100) if p['max_pos'] == 1 \
                    else cash
                q_risk = (budget - 2 * fixed) / risk_ps
                q_cash = (cap_room - fixed) / (ask * (1 + fee))
                qty = math.floor(min(q_risk, q_cash) + 1e-9)
                if qty < 1:
                    continue
                cost = qty * ask
                cash -= cost + cost * fee + fixed
                pos[s] = dict(sym=s, qty=qty, entry=ask, stop=stop, entry_i=t, entry_date=d,
                              in_cost=cost * fee + fixed, risk=qty * risk_ps + 2 * fixed, last=ask)
        # --- intradia: stops ---
        for s in list(pos):
            t = IDX[s].get(d)
            if t is None:
                continue
            b = BARS[s][t]
            ps = pos[s]
            ps['last'] = b['c']
            if b['l'] <= ps['stop']:
                px = min(ps['stop'], b['o']) - slip
                px = max(px, TICK)
                cash += _close(ps, px, d, 'stop', fee, fixed, trades)
                del pos[s]
        eq = cash + sum(ps['qty'] * ps['last'] for ps in pos.values())
        equity.append((d, eq))
        if suspended and not pos:
            pass
    # encerra posicoes abertas ao fim (marcacao, nao simulada como venda)
    open_at_end = {s: dict(qty=ps['qty'], entry=ps['entry'], last=ps['last']) for s, ps in pos.items()}
    return dict(trades=trades, equity=equity, open_at_end=open_at_end, suspended=suspended)


def _close(ps, px, d, why, fee, fixed, trades):
    proceeds = ps['qty'] * px
    out_cost = proceeds * fee + fixed
    net = proceeds - out_cost - (ps['qty'] * ps['entry'] + ps['in_cost'])
    trades.append(dict(sym=ps['sym'], entry_date=ps['entry_date'], exit_date=d, qty=ps['qty'],
                       entry=round(ps['entry'], 4), exit=round(px, 4), why=why,
                       pnl=round(net, 4), costs=round(ps['in_cost'] + out_cost, 4),
                       days=None))
    return proceeds - out_cost


def metrics(res, p, lo=None, hi=None):
    eq = [(d, v) for d, v in res['equity'] if (lo is None or d >= lo) and (hi is None or d <= hi)]
    tr = [t for t in res['trades'] if (lo is None or t['exit_date'] >= lo) and (hi is None or t['exit_date'] <= hi)]
    out = {'n_trades': len(tr)}
    if eq:
        start_v = eq[0][1] if lo else p['capital']
        if lo:   # base = equity do dia anterior ao inicio
            prev = [v for d, v in res['equity'] if d < lo]
            start_v = prev[-1] if prev else p['capital']
        end_v = eq[-1][1]
        peak, mdd = start_v, 0.0
        for _, v in eq:
            peak = max(peak, v)
            mdd = min(mdd, v / peak - 1)
        days = (datetime.fromisoformat(eq[-1][0]) - datetime.fromisoformat(eq[0][0])).days or 1
        ret = end_v / start_v - 1
        out.update(start=round(start_v, 2), end=round(end_v, 2), pnl_eq=round(end_v - start_v, 2),
                   ret_pct=round(ret * 100, 2), max_dd_pct=round(mdd * 100, 2),
                   ann_pct=round(((end_v / start_v) ** (365 / days) - 1) * 100, 2) if days >= 120 and end_v > 0 else None,
                   days=days)
    wins = [t['pnl'] for t in tr if t['pnl'] > 0]
    loss = [t['pnl'] for t in tr if t['pnl'] <= 0]
    out.update(wins=len(wins), losses=len(loss),
               hit_rate=round(len(wins) / len(tr) * 100, 1) if tr else None,
               gross_win=round(sum(wins), 2), gross_loss=round(sum(loss), 2),
               profit_factor=round(sum(wins) / -sum(loss), 2) if loss and sum(loss) < 0 else None,
               avg_win=round(statistics.mean(wins), 3) if wins else None,
               avg_loss=round(statistics.mean(loss), 3) if loss else None,
               expectancy=round(statistics.mean([t['pnl'] for t in tr]), 3) if tr else None,
               net_trades=round(sum(t['pnl'] for t in tr), 2),
               costs=round(sum(t['costs'] for t in tr), 2))
    if tr:
        hold = [(datetime.fromisoformat(t['exit_date']) - datetime.fromisoformat(t['entry_date'])).days for t in tr]
        out['avg_hold_days'] = round(statistics.mean(hold), 1)
        top = sorted((t['pnl'] for t in tr), reverse=True)
        out['top3_pnl'] = round(sum(top[:3]), 2)
    return out


def year_table(res, p):
    ys = {}
    for d, v in res['equity']:
        ys.setdefault(d[:4], []).append(v)
    prev = p['capital']
    out = {}
    for y in sorted(ys):
        out[y] = round((ys[y][-1] / prev - 1) * 100, 2)
        prev = ys[y][-1]
    return out


def bench():
    out = {}
    for s in ('IBOV', 'BOVA11'):
        b = BARS[s]
        for name, (lo, hi) in PERIODS.items():
            seg = [x for x in b if lo <= x['date'] <= hi]
            base = [x for x in b if x['date'] < lo]
            a = base[-1]['c'] if base else seg[0]['o']
            out.setdefault(s, {})[name] = round((seg[-1]['c'] / a - 1) * 100, 2)
        out[s]['total'] = round((b[-1]['c'] / b[0]['c'] - 1) * 100, 2)
    cdi = json.load(open(DATA / 'sgs12_cdi.json'))
    f = 1.0
    per = {k: 1.0 for k in PERIODS}
    for r in cdi:
        dd = datetime.strptime(r['data'], '%d/%m/%Y').strftime('%Y-%m-%d')
        g = 1 + float(r['valor']) / 100
        f *= g
        for k, (lo, hi) in PERIODS.items():
            if lo <= dd <= hi:
                per[k] *= g
    out['CDI'] = {k: round((v - 1) * 100, 2) for k, v in per.items()}
    out['CDI']['total'] = round((f - 1) * 100, 2)
    return out


def full_report(strategy, p, universe=None):
    res = run(strategy, p, universe)
    rep = {'total': metrics(res, p), 'years': year_table(res, p),
           'open_at_end': res['open_at_end'], 'suspended': res['suspended']}
    for name, (lo, hi) in PERIODS.items():
        rep[name] = metrics(res, p, lo, hi)
    return res, rep


def boot_ci(trades, n=5000, seed=7):
    xs = [t['pnl'] for t in trades]
    if len(xs) < 2:
        return None
    rnd = random.Random(seed)
    means = sorted(statistics.mean(rnd.choice(xs) for _ in xs) for _ in range(n))
    return [round(means[int(n * 0.025)], 3), round(means[int(n * 0.975)], 3)]


def main():
    base = default_params()
    out = {'params': base, 'universe': UNIVERSE, 'periods': PERIODS, 'bench': bench(), 'data': {}}
    for s in UNIVERSE + ['IBOV', 'BOVA11']:
        b = BARS[s]
        jumps = [(b[k]['date'], round((b[k]['o'] / b[k - 1]['c'] - 1) * 100, 1)) for k in range(1, len(b))
                 if abs(b[k]['o'] / b[k - 1]['c'] - 1) > 0.15]
        out['data'][s] = dict(first=b[0]['date'], last=b[-1]['date'], bars=len(b), gaps_gt15pct=jumps)
    results = {}
    for strat in ('A', 'B'):
        res, rep = full_report(strat, base)
        rep['bootstrap95_expectancy'] = boot_ci(res['trades'])
        rep['trades'] = res['trades']
        rep['equity_sample'] = res['equity'][::5]
        # por ativo (contribuicao na carteira)
        per = {}
        for t in res['trades']:
            pass
        results[strat] = rep
        # contribuicao por ativo: reexecuta com universo de 1 ativo e max_pos=1 (standalone R$500)
        solo = {}
        for s in UNIVERSE:
            sp = dict(base, max_pos=1)
            r1, m1 = full_report(strat, sp, [s])
            solo[s] = {'ret_pct': m1['total'].get('ret_pct'), 'n': m1['total']['n_trades'],
                       'mdd': m1['total'].get('max_dd_pct'), 'pf': m1['total'].get('profit_factor'),
                       'oos_ret': m1['fora_da_amostra(2025..2026-11-16)'].get('ret_pct')}
        rep['solo_assets'] = solo
        # leave-one-out
        loo = {}
        for s in UNIVERSE:
            _, m = full_report(strat, base, [x for x in UNIVERSE if x != s])
            loo[s] = {'ret_pct': m['total'].get('ret_pct'), 'n': m['total']['n_trades'],
                      'mdd': m['total'].get('max_dd_pct')}
        rep['leave_one_out'] = loo
        # robustez de custos/slippage
        rob = {}
        for name, upd in {'custos x2': dict(cost_mult=2.0), 'custos x4': dict(cost_mult=4.0),
                          'slippage x3': dict(slip_mult=3.0), 'custos x2 + slippage x3': dict(cost_mult=2.0, slip_mult=3.0)}.items():
            _, m = full_report(strat, dict(base, **upd))
            rob[name] = {k: m[k].get('ret_pct') for k in ('total', 'fora_da_amostra(2025..2026-11-16)')}
            rob[name]['mdd'] = m['total'].get('max_dd_pct'); rob[name]['n'] = m['total']['n_trades']
        rep['robust_costs'] = rob
        # sensibilidade de parametros (nenhum escolhido a partir do resultado; so reporta)
        grid = {'A': [dict(atr_mult=1.5), dict(atr_mult=3.0), dict(reg=90), dict(reg=150), dict(zone=20.0), dict(zone=40.0), dict(fast=40), dict(slow=150)],
                'B': [dict(atr_mult=1.5), dict(atr_mult=3.0), dict(brk=15), dict(brk=30), dict(exitlow=7), dict(exitlow=15), dict(rs=40), dict(rs=90)]}[strat]
        sens = []
        for upd in grid:
            _, m = full_report(strat, dict(base, **upd))
            sens.append({'param': upd, 'ret_pct': m['total'].get('ret_pct'), 'oos_ret': m['fora_da_amostra(2025..2026-11-16)'].get('ret_pct'),
                         'mdd': m['total'].get('max_dd_pct'), 'n': m['total']['n_trades'], 'pf': m['total'].get('profit_factor')})
        rep['sensitivity'] = sens
        # capital sem limite de posicoes = 1 (comparacao)
        _, m1 = full_report(strat, dict(base, max_pos=1))
        rep['max_pos_1'] = {k: m1[k] for k in ('total', 'fora_da_amostra(2025..2026-11-16)')}
        # concentracao
        tr = res['trades']
        if tr:
            pnls = sorted((t['pnl'] for t in tr), reverse=True)
            tot = sum(pnls)
            rep['concentration'] = {'n': len(tr), 'net': round(tot, 2), 'top1': pnls[0], 'top3': round(sum(pnls[:3]), 2),
                                    'net_without_top3': round(tot - sum(pnls[:3]), 2)}
        # janelas de queda do IBOV (meses com IBOV < 0): retorno da carteira nesses meses
        ibm = {}
        for b in BARS['IBOV']:
            ibm.setdefault(b['date'][:7], []).append(b['c'])
        eqm = {}
        for d, v in res['equity']:
            eqm.setdefault(d[:7], []).append(v)
        months = sorted(eqm)
        prev_eq, prev_ib = base['capital'], None
        down, up = [], []
        pib = None
        for mo in months:
            e1 = eqm[mo][-1]; i1 = ibm[mo][-1]
            if pib is not None:
                (down if i1 < pib else up).append(e1 / prev_eq - 1)
            prev_eq, pib = e1, i1
        rep['regime'] = {'meses_ibov_queda': len(down), 'ret_medio_nesses_%': round(statistics.mean(down) * 100, 2) if down else None,
                         'meses_ibov_alta': len(up), 'ret_medio_nesses_alta_%': round(statistics.mean(up) * 100, 2) if up else None}
    out['results'] = results
    (ROOT / 'reports/mt5run/results.json').write_text(json.dumps(out, indent=1, default=str), encoding='utf-8')
    for s in ('A', 'B'):
        r = results[s]
        print(s, json.dumps(r['total']), '\n  OOS', json.dumps(r['fora_da_amostra(2025..2026-11-16)']))
    print(json.dumps(out['bench']))


if __name__ == '__main__':
    main()
