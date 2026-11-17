"""Cliente MCP minimo (HTTP) para o terminal MetaTrader 5.

Le a URL e o token do .mcp.json do projeto. Nao envia ordens: so usa
ferramentas de leitura (catalogo de simbolos e historico de candles).
"""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _cfg():
    cfg = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["terminal"]
    return cfg["url"], cfg["headers"]["Authorization"]


class MT5:
    def __init__(self):
        self.url, auth = _cfg()
        self.headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        self._id = 0
        r = self._post({
            "jsonrpc": "2.0", "id": self._next(), "method": "initialize",
            "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "b3-canais", "version": "1"}},
        }, want_session=True)
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _next(self):
        self._id += 1
        return self._id

    def _post(self, body, want_session=False):
        req = urllib.request.Request(self.url, json.dumps(body).encode(), self.headers)
        with urllib.request.urlopen(req, timeout=120) as resp:
            if want_session:
                sid = resp.headers.get("Mcp-Session-Id")
                if sid:
                    self.headers["Mcp-Session-Id"] = sid
            raw = resp.read().decode("utf-8", "replace")
        return json.loads(raw) if raw.strip() else None

    def call(self, name, **args):
        r = self._post({"jsonrpc": "2.0", "id": self._next(), "method": "tools/call",
                        "params": {"name": name, "arguments": args}})
        res = r.get("result", {})
        text = "".join(c.get("text", "") for c in res.get("content", []))
        if res.get("isError"):
            raise RuntimeError(f"{name}: {text}")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
