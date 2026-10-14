"""Fetch indicative intraday FX quotes (5-minute bars, last ~24 h) and write intraday.json.

Runs in GitHub Actions every 10 minutes on weekdays. Source: Yahoo Finance chart API
(unofficial, indicative, may lag a few minutes). Output is published to the `live`
branch and read by the app from raw.githubusercontent.com.
"""
import json, sys, time, urllib.request

SYMBOLS = {"EUR/CZK": "EURCZK=X", "USD/CZK": "USDCZK=X", "EUR/USD": "EURUSD=X", "PLN/CZK": "PLNCZK=X"}
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
SANITY = {"EUR/CZK": (20, 30), "USD/CZK": (15, 30), "EUR/USD": (0.8, 1.5), "PLN/CZK": (4, 7)}


def fetch(symbol):
    last_err = None
    for host in ("query1", "query2"):
        url = f"https://{host}.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=5m&includePrePost=false"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                return json.load(r)["chart"]["result"][0]
        except Exception as e:  # try the other host
            last_err = e
            time.sleep(2)
    raise last_err


def main(out_path):
    now = int(time.time())
    pairs = {}
    for pair, sym in SYMBOLS.items():
        try:
            res = fetch(sym)
        except Exception as e:
            print(f"{pair}: {e}", file=sys.stderr)
            continue
        ts = res.get("timestamp") or []
        closes = (res.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
        lo, hi = SANITY[pair]
        pts = [[t, round(c, 5)] for t, c in zip(ts, closes) if c is not None and lo < c < hi and t >= now - 24 * 3600]
        meta = res.get("meta", {})
        last = meta.get("regularMarketPrice")
        if not pts or last is None or not lo < last < hi:
            print(f"{pair}: no usable data", file=sys.stderr)
            continue
        pairs[pair] = {"last": round(last, 5), "time": meta.get("regularMarketTime") or pts[-1][0],
                       "prevClose": meta.get("chartPreviousClose"), "points": pts}
    if not pairs:
        sys.exit("no pair fetched")
    with open(out_path, "w") as f:
        json.dump({"updated": now, "source": "Yahoo Finance (orientačně)", "pairs": pairs}, f, separators=(",", ":"))
    print("ok", {k: v["last"] for k, v in pairs.items()})


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "intraday.json")
