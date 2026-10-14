"""Indicative intraday FX quotes for the app's 1D chart -> intraday.json.

Runs in GitHub Actions every 10 minutes on weekdays and is published to the `live`
branch, which the app reads from raw.githubusercontent.com.

Sources (all indicative, may lag a few minutes):
1. Yahoo Finance chart API: full 5-minute history for the last 24 h when it answers.
2. TradingView scanner: current price only; appended to the history kept from the
   previous run, so the chart builds up in 10-minute steps even if Yahoo is blocked.
Errors per source are written into the file (field "errors") instead of failing the run.
"""
import json, sys, time, urllib.request

PAIRS = {"EUR/CZK": ("EURCZK=X", "FX_IDC:EURCZK"), "USD/CZK": ("USDCZK=X", "FX_IDC:USDCZK"),
         "EUR/USD": ("EURUSD=X", "FX_IDC:EURUSD"), "PLN/CZK": ("PLNCZK=X", "FX_IDC:PLNCZK")}
SANITY = {"EUR/CZK": (20, 30), "USD/CZK": (15, 30), "EUR/USD": (0.8, 1.5), "PLN/CZK": (4, 7)}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
WINDOW = 24 * 3600


def http_json(url, data=None):
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=20) as r:
        return json.load(r)


def yahoo(symbol):
    last_err = None
    for host in ("query1", "query2"):
        try:
            res = http_json(f"https://{host}.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=5m")["chart"]["result"][0]
            ts = res.get("timestamp") or []
            closes = (res.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
            return [[t, c] for t, c in zip(ts, closes) if c is not None]
        except Exception as e:
            last_err = e
            time.sleep(1)
    raise RuntimeError(f"yahoo {symbol}: {last_err}")


def tradingview():
    body = {"symbols": {"tickers": [tv for _, tv in PAIRS.values()]}, "columns": ["close"]}
    rows = http_json("https://scanner.tradingview.com/forex/scan", body).get("data", [])
    return {r["s"]: r["d"][0] for r in rows if r.get("d") and r["d"][0] is not None}


def main(out_path, prev_path):
    now = int(time.time())
    errors = []
    try:
        prev = json.load(open(prev_path)).get("pairs", {})
    except Exception:
        prev = {}
    try:
        tv = tradingview()
    except Exception as e:
        tv = {}
        errors.append(f"tradingview: {e}")

    out = {}
    for pair, (ysym, tsym) in PAIRS.items():
        lo, hi = SANITY[pair]
        ok = lambda v: v is not None and lo < v < hi
        pts = []
        try:
            pts = [[t, round(c, 5)] for t, c in yahoo(ysym) if ok(c)]
        except Exception as e:
            errors.append(str(e)[:200])
        if not pts:  # keep our own history from previous runs
            pts = [p for p in prev.get(pair, {}).get("points", []) if ok(p[1])]
        if ok(tv.get(tsym)):
            pts.append([now, round(tv[tsym], 5)])
        pts = sorted({p[0]: p for p in pts if p[0] >= now - WINDOW}.values())
        if pts:
            out[pair] = {"last": pts[-1][1], "time": pts[-1][0], "points": pts}

    with open(out_path, "w") as f:
        json.dump({"updated": now, "source": "Yahoo Finance / TradingView (orientačně)", "pairs": out,
                   "errors": errors}, f, separators=(",", ":"))
    print("pairs:", {k: (v["last"], len(v["points"])) for k, v in out.items()})
    print("errors:", errors)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "intraday.json", sys.argv[2] if len(sys.argv) > 2 else "prev.json")
