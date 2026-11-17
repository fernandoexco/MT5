"""Coleta D1 (somente leitura) do MT5 para o backtest consolidado A/B."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from mt5mcp import MT5
OUT = pathlib.Path(__file__).resolve().parent.parent / 'reports/mt5run/data'
SYMS = "ITUB4 BBAS3 WEGE3 GGBR4 PETR4 VALE3 BBDC4 ABEV3 EGIE3 SUZB3 BOVA11 IBOV".split()
m = MT5(); info = {}
for s in SYMS:
    added = False
    try:
        try:
            m.call('get_chart_history', symbol=s, period='D1', datetime_from='2026-11-01T00:00:00', datetime_to='2026-11-17T00:00:00', limit=5)
        except RuntimeError:
            m.call('add_marketwatch_symbol', symbol=s); added = True
        r = m.call('get_chart_history', symbol=s, period='D1',
                   datetime_from='2020-01-01T00:00:00', datetime_to='2026-11-17T00:00:00', limit=5000)
        rows = r.get('candles') or r.get('bars') or r.get('records') or r
        (OUT / f'{s}.json').write_text(json.dumps(r), encoding='utf-8')
        info[s] = (type(r).__name__, list(r)[:6] if isinstance(r, dict) else len(r))
    except Exception as e:
        info[s] = 'ERRO ' + str(e)[:150]
    finally:
        if added:
            try: m.call('remove_marketwatch_symbol', symbol=s)
            except Exception as e: info[s+'_remove'] = str(e)[:100]
print(json.dumps(info, indent=1, default=str))
