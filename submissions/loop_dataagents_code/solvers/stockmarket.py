#!/usr/bin/env python3
"""stockmarket q1-q4 deterministic solver — implements frozen/stockmarket_readings.md
(preregistered 2026-11-09T07:30Z). No LLM calls. Stores: stockinfo_query.db (sqlite),
stocktrade_query.db (duckdb, one table per symbol).
"""
import json, re, sqlite3, sys, time
from datetime import date

import duckdb

INFO = "/root/dabdata/query_stockmarket/query_dataset/stockinfo_query.db"
TRADE = "/root/dabdata/query_stockmarket/query_dataset/stocktrade_query.db"

VERBS = (r"provides|offers|is|operates|develops|manufactures|sells|engages|focuses|"
         r"specializes|delivers|creates|produces|supplies|designs|markets|distributes|"
         r"owns|runs|manages|builds|enables|allows|helps|gives|serves|acquires|invests|"
         r"seeks|works|participates|partners|licens\w*|has|utilizes|excels|crafts|are|"
         r"empowers|harnesses|based")
NAME_RE = re.compile(rf"^(.{{2,120}}?)\s+({VERBS})\b")

def company_name(desc):
    if not desc:
        return None
    m = NAME_RE.match(desc)
    if not m:
        return None
    n = m.group(1).strip().rstrip(",")
    return n if n else None

diag = {"unmatched_name": []}
info = sqlite3.connect(f"file:{INFO}?mode=ro", uri=True)
tickers = {}  # symbol -> dict
for sym, etf, lex, mc, fs, desc in info.execute(
    'select Symbol, ETF, "Listing Exchange", "Market Category", "Financial Status",'
    ' "Company Description" from stockinfo'):
    nm = company_name(desc)
    if nm is None:
        diag["unmatched_name"].append(sym)
    tickers[sym] = {"etf": etf, "exch": lex, "cat": mc, "fs": fs, "name": nm}
info.close()
diag["tickers"] = len(tickers)

dj = duckdb.connect(TRADE, read_only=True)
tables = {r[0] for r in dj.execute("show tables").fetchall()}
diag["trade_tables"] = len(tables)

def q(s):  # quote identifier
    return '"' + s.replace('"', '""') + '"'

def nm(name):  # reporting form: parsed name without trailing period
    return (name or "").rstrip(".")

# ---------------- q1 ----------------
rr = [s for s, t in tickers.items()
      if t["name"] and t["name"].rstrip(", Inc.Company ") != ""
      and re.sub(r"[,\s]+(Inc|Corp|Corporation|Company|Co|Ltd|LLC|PLC|Incorporated)\.?$", "",
                 t["name"]).strip() == "The RealReal"]
diag["q1_realreal_symbols"] = rr
q1_answer = "0"
if len(rr) == 1 and rr[0] in tables:
    v = dj.execute(f'select max("Adj Close") from {q(rr[0])} where Date between \'2020-01-01\' and \'2020-12-31\'').fetchone()[0]
    q1_answer = f"{round(v, 2)}"

# ---------------- q2 ----------------
q2_syms = []
for s, t in tickers.items():
    if t["etf"] == "Y" and t["exch"] == "P" and s in tables:
        v = dj.execute(f'select max("Adj Close") from {q(s)} where Date between \'2015-01-01\' and \'2015-12-31\'').fetchone()[0]
        if v is not None and v > 200:
            q2_syms.append(s)
q2_syms.sort()
q2_lines = [f"{s}: {nm(tickers[s]['name'])}" for s in q2_syms]
q2_lines.append(f"Total number of such ETFs: {len(q2_syms)}")
q2_answer = "\n".join(q2_lines)

# ---------------- q3 ----------------
q3_rows = []
for s, t in tickers.items():
    if t["fs"] not in ("D", "E", "H"):
        continue
    if t["cat"] not in ("Q", "G", "S"):
        continue
    if s not in tables or t["name"] is None:
        continue
    r = dj.execute(f"select count(Volume), avg(Volume) from {q(s)} where Date between '2008-01-01' and '2008-12-31' and Volume is not null").fetchone()
    if r[0] > 0 and r[1] is not None:
        q3_rows.append((t["name"], r[0], r[1], s))
q3_rows.sort(key=lambda x: (-x[2], x[0]))
diag["q3_rows"] = [(n, c) for n, c, _, _ in q3_rows]
q3_answer = "\n".join(f"{nm(n)} ({sym}): average daily volume {a:.2f} over {c} trading days"
                      for n, c, a, sym in q3_rows)

# ---------------- q4 ----------------
q4_cands = []
for s, t in tickers.items():
    if t["etf"] == "N" and t["exch"] == "N" and s in tables and t["name"]:
        q4_cands.append(s)
diag["q4_candidates"] = len(q4_cands)
scored = []
for s in q4_cands:
    # R015 (2026-11-10): question text defines up/down days as close vs OPEN
    # (not close vs previous close). Count intraday moves for 2017 only.
    rows = dj.execute(f"select Date, Open, Close from {q(s)} where Date between '2017-01-01' and '2017-12-31' order by Date").fetchall()
    up = down = 0
    for _dt, o, c in rows:
        if o is None or c is None:
            continue
        if c > o:
            up += 1
        elif c < o:
            down += 1
    if up > down:
        scored.append((up - down, s, up, down, tickers[s]["name"]))
scored.sort(key=lambda t: (-t[0], t[1]))
diag["q4_top10"] = scored[:10]
q4_top = scored[:5]
q4_answer = "\n".join(f"{i+1}. {nm(x[4])} ({x[1]}) - {x[2]} up days, {x[3]} down days"
                      for i, x in enumerate(q4_top))

# ---------------- q5 ----------------
q5_scored = []
for s, t in tickers.items():
    if t["cat"] != "S" or s not in tables or not t["name"]:
        continue
    r = dj.execute(f"select count(*) from {q(s)} where Date between '2019-01-01' and '2019-12-31'"
                   f" and High is not null and Low is not null and Low > 0 and (High - Low) / Low > 0.20").fetchone()
    q5_scored.append((r[0], s, t["name"]))
q5_scored.sort(key=lambda x: (-x[0], x[1]))
diag["q5_top10"] = q5_scored[:10]
q5_top = q5_scored[:5]
q5_answer = "\n".join(f"{i+1}. {nm(x[2])} ({x[1]}) - {x[0]} qualifying days"
                      for i, x in enumerate(q5_top))

result = {
    "dataset": "stockmarket",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "q1_answer": q1_answer, "q2_answer": q2_answer,
    "q3_answer": q3_answer, "q4_answer": q4_answer, "q5_answer": q5_answer,
    "q2_symbols": q2_syms, "q4_top": q4_top, "q5_top": q5_top,
    "diagnostics": diag,
}
out = sys.argv[1] if len(sys.argv) > 1 else "/root/dabteam/runs/stockmarket/result.json"
json.dump(result, open(out, "w"), indent=2, ensure_ascii=False)
answers = {"1": q1_answer, "2": q2_answer, "3": q3_answer, "4": q4_answer, "5": q5_answer}
entries = [{"dataset": "stockmarket", "query": qi, "run": run, "answer": answers[qi]}
           for qi in map(str, range(1, 6)) for run in range(5)]
ej = out.replace("result.json", "entries.json")
json.dump(entries, open(ej, "w"), indent=2, ensure_ascii=False)
print(json.dumps(result, indent=2, ensure_ascii=False))
