#!/usr/bin/env python3
"""stockindex q1-q3 deterministic solver — implements frozen/stockindex_readings.md
(preregistered 2026-11-09T07:15Z). No LLM calls. Stores: indexInfo_query.db (sqlite),
indextrade_query.db (duckdb). Mixed date formats normalised per row.
"""
import json, re, sqlite3, sys, time
from collections import defaultdict
from datetime import datetime

import duckdb

INFO = "/root/dabdata/query_stockindex/query_dataset/indexInfo_query.db"
TRADE = "/root/dabdata/query_stockindex/query_dataset/indextrade_query.db"

EXCH2SYM = {
    "New York Stock Exchange": "NYA", "NASDAQ": "IXIC",
    "Hong Kong Stock Exchange": "HSI", "Shanghai Stock Exchange": "000001.SS",
    "Tokyo Stock Exchange": "N225", "Euronext": "N100",
    "Shenzhen Stock Exchange": "399001.SZ", "Toronto Stock Exchange": "GSPTSE",
    "National Stock Exchange of India": "NSEI",
    "Frankfurt Stock Exchange": "GDAXI", "SIX Swiss Exchange": "SSMI",
    "Taiwan Stock Exchange": "TWII", "Johannesburg Stock Exchange": "J203.JO",
}  # Korea Exchange: no symbol in index_trade -> inner join drops
REGION = {"HSI": "Asia", "000001.SS": "Asia", "399001.SZ": "Asia", "N225": "Asia",
          "NSEI": "Asia", "TWII": "Asia", "NYA": "North America",
          "IXIC": "North America", "GSPTSE": "North America", "N100": "Europe",
          "GDAXI": "Europe", "SSMI": "Europe", "J203.JO": "Africa"}
COUNTRY = {"NYA": "United States", "IXIC": "United States", "N225": "Japan",
           "GDAXI": "Germany", "GSPTSE": "Canada", "HSI": "Hong Kong",
           "SSMI": "Switzerland", "N100": "France", "000001.SS": "China",
           "399001.SZ": "China", "NSEI": "India", "TWII": "Taiwan", "J203.JO": "South Africa"}

FORMATS = ["%d %b %Y, %H:%M", "%B %d, %Y at %I:%M %p", "%Y-%m-%d %H:%M:%S",
           "%d %b %Y %H:%M", "%B %d, %Y", "%d %b %Y", "%Y-%m-%d"]

def parse_date(s):
    s = s.strip()
    for f in FORMATS:
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            continue
    return None

diag = {}
info = sqlite3.connect(f"file:{INFO}?mode=ro", uri=True)
exchanges = {r[0] for r in info.execute("select Exchange from index_info")}
info.close()
diag["exchanges"] = len(exchanges)
sym2exch = {v: k for k, v in EXCH2SYM.items() if k in exchanges}

dj = duckdb.connect(TRADE, read_only=True)
rows = dj.execute("select Index, Date, Open, High, Low, Close, \"Adj Close\", CloseUSD from index_trade").fetchall()
dj.close()
diag["trade_rows"] = len(rows)
by_sym = defaultdict(list)
bad_dates = 0
for sym, ds, o, h, l, c, adj, cusd in rows:
    d = parse_date(ds)
    if d is None:
        bad_dates += 1
        continue
    by_sym[sym].append((d, o, h, l, c, adj, cusd))
diag["bad_dates"] = bad_dates
for s in by_sym:
    by_sym[s].sort(key=lambda t: t[0])

# ---------------- q1 ----------------
asia = [s for s in by_sym if REGION.get(s) == "Asia"]
vol = {}
for s in asia:
    vals = [(h - l) / o for d, o, h, l, c, adj, cusd in by_sym[s]
            if d >= datetime(2020, 1, 1).date() and o]
    if vals:
        vol[s] = sum(vals) / len(vals)
diag["q1_asia_2020_days"] = {s: sum(1 for d, *_ in by_sym[s] if d.year >= 2020) for s in asia}
q1 = max(vol.items(), key=lambda kv: (kv[1], kv[0]))
diag["q1_avg_vol"] = vol
q1_answer = (f"{q1[0]} ({sym2exch[q1[0]]}, {COUNTRY[q1[0]]}) - "
             f"highest average intraday volatility since 2020 ({q1[1]:.4f})")

# ---------------- q2 ----------------
na = [s for s in by_sym if REGION.get(s) == "North America"]
q2_hits = []
for s in na:
    up = sum(1 for d, o, h, l, c, adj, cusd in by_sym[s]
             if d.year == 2018 and c is not None and o is not None and c > o)
    down = sum(1 for d, o, h, l, c, adj, cusd in by_sym[s]
               if d.year == 2018 and c is not None and o is not None and c < o)
    diag.setdefault("q2UpDown", {})[s] = (up, down)
    if up > down:
        q2_hits.append((s, up, down))
q2_hits.sort(key=lambda t: t[0])
q2_answer = "\n".join(
    f"{s} ({sym2exch[s]}, {COUNTRY[s]}) - {u} up days vs {d} down days"
    for s, u, d in q2_hits)

# ---------------- q3 ----------------
# "regular monthly investments in all indices since 2000": every index present in
# index_info participates; months start at 2000-01 or the index's first available month.
cands = [s for s in by_sym if sym2exch.get(s)]
diag["q3_candidates"] = cands
rets = {}
for s in cands:
    first_by_month = {}
    for rec in by_sym[s]:
        d = rec[0]
        if d < datetime(2000, 1, 1).date():
            continue
        mk = (d.year, d.month)
        if mk not in first_by_month:
            first_by_month[mk] = rec
    months = sorted(first_by_month)
    shares = 0.0
    for mk in months:
        cusd = first_by_month[mk][6]
        if cusd:
            shares += 1.0 / cusd
    last = by_sym[s][-1]
    end_month = (last[0].year, last[0].month)
    # value at the last available trading day's CloseUSD
    value = shares * (last[6] if last[6] else 0)
    invested = len(months)
    if invested:
        rets[s] = value / invested - 1
    diag.setdefault("q3_detail", {})[s] = {
        "months": invested, "first_month": months[0] if months else None,
        "last_day": str(last[0]), "return": rets.get(s)}
ranked = sorted(rets.items(), key=lambda kv: (-kv[1], kv[0]))
q3_top = ranked[:5]
q3_answer = "\n".join(
    f"{i+1}. {s} ({COUNTRY[s]}) - overall return {r*100:.2f}% over "
    f"{diag['q3_detail'][s]['months']} monthly investments"
    for i, (s, r) in enumerate(q3_top))

result = {
    "dataset": "stockindex",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "q1_answer": q1_answer, "q1_avg_vol": q1[1],
    "q2_answer": q2_answer, "q2_hits": q2_hits,
    "q3_answer": q3_answer, "q3_top": q3_top,
    "diagnostics": diag,
}
out = sys.argv[1] if len(sys.argv) > 1 else "/root/dabteam/runs/stockindex/result.json"
json.dump(result, open(out, "w"), indent=2, ensure_ascii=False)
print(json.dumps(result, indent=2, ensure_ascii=False))
