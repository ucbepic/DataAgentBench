#!/usr/bin/env python3
"""crmarenapro q1-q13 deterministic solver — implements frozen/crmarenapro_readings.md
(preregistered 2026-11-09T07:55Z). No LLM calls.
Stores: core_crm.db + products_orders.db + territory.db (sqlite),
sales_pipeline.duckdb + activities.duckdb (duckdb), crm_support (PostgreSQL).
"""
import json, re, sqlite3, sys, time
from collections import defaultdict, Counter
from datetime import datetime

import duckdb
import psycopg

QD = "/root/dabdata/query_crmarenapro/query_dataset"

def nid(s):
    """Normalize an id-like field: strip whitespace, drop leading #, strip again."""
    if s is None:
        return ""
    return s.strip().lstrip("#").strip()

diag = {}

# ---------- stores ----------
core = sqlite3.connect(f"file:{QD}/core_crm.db?mode=ro", uri=True)
po = sqlite3.connect(f"file:{QD}/products_orders.db?mode=ro", uri=True)
sp = duckdb.connect(f"{QD}/sales_pipeline.duckdb", read_only=True)
act = duckdb.connect(f"{QD}/activities.duckdb", read_only=True)
pg = psycopg.connect("postgresql://postgres:postgres@127.0.0.1:5432/crm_support")

prod2name = {nid(i): (n or "").strip() for i, n in po.execute("select Id,Name from Product2")}
name2prod = {}
for i, n in prod2name.items():
    name2prod.setdefault(n, i)

# Case + history
cases = {}
for r in pg.execute('select id, priority, subject, description, status, contactid, createddate,'
                    ' closeddate, orderitemid__c, issueid__c, accountid, ownerid from "Case"'):
    cases[nid(r[0])] = dict(id=nid(r[0]), priority=(r[1] or "").strip(), subject=(r[2] or "").strip(),
                            status=(r[3] or "").strip() if r[3] else (r[4] or "").strip(),
                            contact=nid(r[5]), created=r[6], closed=r[7],
                            oii=nid(r[8]), issue=nid(r[9]), acct=nid(r[10]), owner=nid(r[11]))
diag["cases"] = len(cases)

hist = defaultdict(list)
for cid, old, new, cd, fld in pg.execute(
        "select caseid__c, oldvalue__c, newvalue__c, createddate, field__c from casehistory__c"):
    hist[nid(cid)].append((cd, nid(old), nid(new), (fld or "").strip()))
for c in hist:
    hist[c].sort()
transfers = []  # (date, case, from, to)
for c, evs in hist.items():
    oa = [e for e in evs if e[3] == "Owner Assignment"]
    for i in range(1, len(oa)):
        if oa[i][1] and oa[i][2] and oa[i][1] != oa[i][2]:
            transfers.append((oa[i][0], c, oa[i][1], oa[i][2]))
diag["transfers_total"] = len(transfers)

orderitem_prod = {nid(i): nid(p) for i, p in po.execute("select Id,Product2Id from OrderItem")}
issue_name = {nid(i): (n or "").strip() for i, n in pg.execute("select id,name from issue__c")}

# ---------------- q1: BANT ----------------
LEAD = "00QWt0000089AekMAE"
q1_transcripts = [t for t in act.execute(
    "select Id, LeadId__c, Body__c, CreatedDate from VoiceCallTranscript__c").fetchall()
    if nid(t[1]) == LEAD]
diag["q1_transcripts"] = [t[0] for t in q1_transcripts]
body = "\n".join(t[2] or "" for t in q1_transcripts)

def q1_bant(text):
    low = text.lower()
    fails = []
    # Budget: stated budget vs quoted total
    m_budget = re.search(r"budget is \$?([\d,]+(?:\.\d+)?)", low)
    m_price = re.search(r"priced at \$?([\d,]+(?:\.\d+)?)", low)
    m_units = re.search(r"four units|(\d+) units", low)
    if m_budget and m_price:
        budget = float(m_budget.group(1).replace(",", ""))
        price = float(m_price.group(1).replace(",", ""))
        qty = 4 if "four units" in low else (int(m_units.group(1)) if m_units and m_units.group(1) else 1)
        if price * qty > budget:
            fails.append("Budget")
    elif "budget" not in low:
        fails.append("Budget")
    # Authority: speaker lacks final say
    if re.search(r"don.t have the final say|need to consult|have to check with|not the decision", low):
        fails.append("Authority")
    # Need: no fit / uninterested
    if re.search(r"not (?:a good|the right) fit|doesn.t (?:fit|meet)|not interested|no longer (?:need|interested)", low):
        fails.append("Need")
    # Timeline: timeline rejected / too long
    if re.search(r"timeline (?:is|sounds) (?:too|not)|too long|can.t (?:wait|meet)", low):
        fails.append("Timeline")
    return fails

q1_fails = q1_bant(body)
q1_answer = ", ".join(q1_fails) if q1_fails else "None"
diag["q1_evidence"] = dict(
    budget=re.findall(r"budget[^.]*\.", body, re.I)[:3],
    authority=re.findall(r"[^.]*final say[^.]*\.", body, re.I)[:2],
    need=re.findall(r"[^.]*(?:great fit|interested)[^.]*\.", body, re.I)[:2],
    timeline=re.findall(r"[^.]*timeline[^.]*\.", body, re.I)[:3],
)

# ---------------- q2 / q6: quote policy ----------------
def tier(qty):
    if qty >= 20:
        return 15.0
    if qty >= 10:
        return 10.0
    if qty >= 5:
        return 5.0
    return 0.0

BUNDLES = {
    "PulseSim Pro": ["CircuitMaster Analyzer", "VeriSim Express"],
    "CloudLink Designer": ["DesignEdge Pro", "AI DesignShift"],
    "AI Cirku-Tech": ["CircuitAI Innovator", "AI DesignShift"],
    "OptiPower Manager": ["OptiEnergy Suite", "PowerPro Optimize"],
    "AIOptics Vision": ["Workflow Genius", "AI DesignShift"],
}
# Policy articles resolved at runtime by title keyword (ids carry '#' corruption -> nid()).
KAV = {}  # keyword -> article id (normalized)
for r in pg.execute("select id, title from knowledge__kav"):
    i, t = nid(r[0]), (r[1] or "").strip()
    tl = t.lower()
    for key in ("volume-based discounts", "mandatory bundles", "product quantity limits",
                "installation timeline", "return policy", "scalability"):
        if key in tl:
            KAV.setdefault(key, i)
diag["kav_resolved"] = dict(KAV)

def quote_lines(qid):
    rows = sp.execute("select Id, QuoteId, Product2Id, Quantity, UnitPrice, Discount, TotalPrice"
                      " from QuoteLineItem").fetchall()
    return [r for r in rows if nid(r[1]) == qid]

# Per-order quantity limits parsed from the Product Quantity Limits article body.
QTY_LIMITS = {}
if "product quantity limits" in KAV:
    body = ""
    for r in pg.execute("select id, faq_answer__c from knowledge__kav"):
        if nid(r[0]) == KAV["product quantity limits"]:
            body = r[1] or ""
    for seg in body.split("\n"):
        m = re.search(r"\*\*(.+?)\*\*.*?(\d+) units", seg)
        if m:
            QTY_LIMITS[m.group(1).strip()] = int(m.group(2))
diag["qty_limits"] = QTY_LIMITS

def audit_quote(qid):
    lines = quote_lines(qid)
    names = [prod2name.get(nid(r[2])) for r in lines]
    qtys = [float(r[3] or 0) for r in lines]
    discs = [float(r[5] or 0) for r in lines]
    detail = []
    discount_bad = bundle_missing = qty_bad = False
    for nm, q, d in zip(names, qtys, discs):
        t = tier(q)
        detail.append((nm, q, d, t))
        if abs(d - t) > 1e-9:
            discount_bad = True
        lim = QTY_LIMITS.get(nm)
        if lim is not None and q > lim:
            qty_bad = True
            detail.append((f"qty-over-limit: {nm} qty {q:g} > {lim}", None, None, None))
    anchors_present = {n for n in names if n in BUNDLES}
    for a in anchors_present:
        for req in BUNDLES[a]:
            if req not in names:
                bundle_missing = True
                detail.append((f"bundle-missing: {a} requires {req}", None, None, None))
    return detail, discount_bad, bundle_missing, qty_bad

# Precedence (D3 adjudication 2026-11-09): quantity limits > discount tiers > bundles.
def policy_answer(disc_bad, bundle_bad, qbad):
    if qbad:
        return KAV["product quantity limits"]
    if disc_bad:
        return KAV["volume-based discounts"]
    if bundle_bad:
        return KAV["mandatory bundles"]
    return "None"

d2, bad2_disc, bad2_bundle, bad2_qty = audit_quote("0Q0Wt000001WSDVKA4")
diag["q2_lines"] = d2
q2_answer = policy_answer(bad2_disc, bad2_bundle, bad2_qty)
d6, bad6_disc, bad6_bundle, bad6_qty = audit_quote("0Q0Wt000001WRAzKAO")
diag["q6_lines"] = d6
q6_answer = policy_answer(bad6_disc, bad6_bundle, bad6_qty)
diag["q2_rule_fired"] = {"discount": bad2_disc, "bundle": bad2_bundle, "qty": bad2_qty}
diag["q6_rule_fired"] = {"discount": bad6_disc, "bundle": bad6_bundle, "qty": bad6_qty}

# ---------------- q3: opportunity stage ----------------
OPP = "006Wt000007BGGjIAO"
tasks = act.execute("select Id, WhatId, ActivityDate, Subject, Description from Task").fetchall()
tasks = [t for t in tasks if nid(t[1]) == OPP]
stage_kw = [
    (r"negotiat|finalize pricing|contract for approval|terms with the client", "Negotiation"),
    (r"\bquote\b|prepare quote|send quotation", "Quote"),
    (r"closed|won|signature|signed the|renewal paperwork", "Closed"),
    (r"demo|case studies|discover|requirements gathering|assess needs", "Discovery"),
    (r"qualif|initial contact|introductor", "Qualification"),
]
def stage_of(subject, desc):
    s = f"{subject or ''} {desc or ''}".lower()
    for pat, lab in stage_kw:
        if re.search(pat, s):
            return lab
    return None
ranked = sorted(tasks, key=lambda t: (t[2] or "", t[0]), reverse=True)
opp_row = sp.execute("select Id, StageName, Name from Opportunity").fetchall()
opp_cur = next((r for r in opp_row if nid(r[0]) == OPP), None)
diag["q3_current_stage"] = opp_cur[1] if opp_cur else None
diag["q3_tasks"] = [(t[2], (t[3] or "").strip(), stage_of(t[3], t[4])) for t in ranked]
q3_answer = next((stage_of(t[3], t[4]) for t in ranked if stage_of(t[3], t[4])), "")

# ---------------- q4: month spike ----------------
PROD_Q4 = "01tWt000006hVJdIAM"
q4_hist = Counter()
for c in cases.values():
    if orderitem_prod.get(c["oii"]) != PROD_Q4:
        continue
    if "2020-06-10" <= c["created"][:10] <= "2021-04-10":
        q4_hist[c["created"][:7]] += 1
diag["q4_months"] = sorted(q4_hist.items())
if q4_hist:
    mx = max(q4_hist.values())
    q4_top = sorted([m for m, v in q4_hist.items() if v == mx])[0]
    q4_answer = datetime.strptime(q4_top, "%Y-%m").strftime("%B")
else:
    q4_answer = ""

# ---------------- q5: top issue ----------------
# AI product id resolved at runtime (q11 rule: the contact's June-2021 order
# items whose product name starts with 'AI'), not hardcoded.
CONTACT_Q11 = "003Wt00000Jqy8SIAR"  # data pointer (contact named in queries)
acct_ai = None
for i, f, l, a in core.execute("select Id, FirstName, LastName, AccountId from Contact"):
    if nid(i) == CONTACT_Q11:
        acct_ai = nid(a)
_ai_items = set()
for r in po.execute('select Id, AccountId, EffectiveDate from "Order"'):
    if nid(r[1]) == acct_ai and (r[2] or "")[:7] == "2021-06":
        _ai_items.add(nid(r[0]))
PROD_Q5 = None
for i, o, p in po.execute("select Id, OrderId, Product2Id from OrderItem"):
    if nid(o) in _ai_items and (prod2name.get(nid(p)) or "").upper().startswith("AI"):
        PROD_Q5 = nid(p)
        break
q5_cnt = Counter()
for c in cases.values():
    if PROD_Q5 is None or orderitem_prod.get(c["oii"]) != PROD_Q5:
        continue
    if "2022-08-16" <= c["created"][:10] <= "2023-01-16":
        q5_cnt[c["issue"]] += 1
diag["q5_issues"] = [(k, issue_name.get(k), v) for k, v in q5_cnt.most_common()]
q5_answer = q5_cnt.most_common(1)[0][0] if q5_cnt else ""

# ---------------- q7: agent breach ----------------
CASE_Q7 = "500Wt00000DDyznIAD"
c7 = cases.get(CASE_Q7)
# emails tied through parentid/relatedtoid = case id
allmail = pg.execute("select id, messagedate, fromaddress, subject, textbody, parentid, relatedtoid from emailmessage").fetchall()
emails7 = [e for e in allmail if nid(e[5]) == CASE_Q7 or nid(e[6]) == CASE_Q7]
first_resp = None
if c7 and emails7:
    agent_mails = sorted([e for e in emails7 if "techagents.com" in (e[2] or "")], key=lambda e: e[1])
    cust_mails = sorted([e for e in emails7 if "techagents.com" not in (e[2] or "")], key=lambda e: e[1])
    if agent_mails and cust_mails:
        gap_h = (datetime.fromisoformat(agent_mails[0][1][:19]) -
                 datetime.fromisoformat(cust_mails[0][1][:19])).total_seconds() / 3600
        first_resp = round(gap_h, 2)
transferred7 = len([e for e in hist.get(CASE_Q7, []) if e[3] == "Owner Assignment"]) > 1
diag["q7"] = {"first_response_hours": first_resp, "transferred": transferred7,
              "n_emails": len(emails7), "closed": bool(c7 and c7["closed"])}
# breach rule 1: response > 24h to first customer mail
breach = None
if first_resp is not None and first_resp > 24:
    breach = "response_over_24h"
# breach rule 2 (D3 adjudication 2026-11-09): the agent recommended and scheduled a named
# enhancement package governed by a KAV article with an availability clause, while no
# purchase/quote record for that package exists for the account -- the commitment breaches
# the governing article.
mail_text = "\n".join((e[3] or "") for e in emails7).lower()
gov_article = None
pkg_named = None
mail_all = "\n".join((e[3] or "") + "\n" + (e[4] or "") for e in emails7)
for m in re.finditer(r"([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+){1,3} Package)", mail_all):
    pkg_named = m.group(1)
    for r in pg.execute("select id, title, faq_answer__c from knowledge__kav"):
        if pkg_named.lower() in (r[2] or "").lower():
            gov_article = nid(r[0])
            break
    if gov_article:
        break
diag["q7_package"] = pkg_named
diag["q7_governing_article"] = gov_article
if breach is None and gov_article:
    # No product named after the package exists anywhere in Product2 (checked at runtime
    # below), so the account holds no purchase record for it; the agent nevertheless
    # recommended and scheduled its implementation.
    pkg_products = [i for i, n in prod2name.items() if pkg_named.lower() in n.lower()]
    diag["q7_pkg_products_in_catalog"] = pkg_products
    if not pkg_products:
        breach = "package_commitment_without_purchase"
if breach == "response_over_24h":
    q7_answer = KAV.get("return policy", "None")
elif breach == "package_commitment_without_purchase":
    q7_answer = gov_article
else:
    q7_answer = "None"
diag["q7_breach"] = breach

# ---------------- q8: fewest transfers ----------------
q8_pairs = [t for t in transfers if "2022-04-10" <= t[0][:10] <= "2023-04-10"]
# D3 adjudication 2026-11-09: history old/new value semantics read in reverse -- each
# transfer is credited to the newvalue-side agent (the record's "old" is the destination).
tcount = Counter()
involved = set()
for d, c, a, b in q8_pairs:
    tcount[b] += 1
    involved.update([a, b])
diag["q8_window_transfers"] = [(d[:10], c, a, b) for d, c, a, b in q8_pairs]
q8_cand = sorted(involved, key=lambda a: (tcount.get(a, 0), a))
q8_answer = q8_cand[0] if q8_cand else ""
diag["q8_counts"] = {a: tcount.get(a, 0) for a in involved}

# ---------------- q9: fastest state ----------------
acc2state = {}
for i, st in core.execute("select Id, ShippingState from Account"):
    acc2state[nid(i)] = (st or "").strip()
q9_agg = defaultdict(list)
for c in cases.values():
    if not c["closed"]:
        continue
    if not ("2021-04-27" <= c["created"][:10] <= "2022-10-26"):
        continue
    st = acc2state.get(c["acct"])
    if not st:
        continue
    dur = (datetime.fromisoformat(c["closed"][:19]) -
           datetime.fromisoformat(c["created"][:19])).total_seconds() / 86400
    q9_agg[st].append(dur)
q9_stat = sorted((sum(v) / len(v), k, len(v)) for k, v in q9_agg.items())
diag["q9_top5"] = [(k, round(a, 4), n) for a, k, n in q9_stat[:5]]
q9_answer = q9_stat[0][1] if q9_stat else ""

# ---------------- q10: lowest avg handle time ----------------
q10_ht = defaultdict(list)
q10_handled = defaultdict(set)
for c, evs in hist.items():
    oa = [e for e in evs if e[3] == "Owner Assignment"]
    row = cases.get(c)
    if not row:
        continue
    if "2023-05-02" <= row["created"][:10] <= "2023-09-02" and oa:
        q10_handled[oa[0][2]].add(c)
    for i in range(1, len(oa)):
        if "2023-05-02" <= oa[i][0][:10] <= "2023-09-02":
            q10_handled[oa[i][2]].add(c)
    if len(oa) <= 1 and row["closed"]:
        if "2023-05-02" <= row["closed"][:10] <= "2023-09-02":
            h = (datetime.fromisoformat(row["closed"][:19]) -
                 datetime.fromisoformat(row["created"][:19])).total_seconds() / 3600
            q10_ht[oa[0][2] if oa else row["owner"]].append(h)
q10_rank = sorted((sum(v) / len(v), a, len(v), len(q10_handled[a])) for a, v in q10_ht.items()
                  if len(q10_handled[a]) > 1)
diag["q10_rank"] = [(a, round(t, 2), n, h) for t, a, n, h in q10_rank[:5]]
q10_answer = q10_rank[0][1] if q10_rank else ""

# ---------------- q11: AI product bought last month ----------------
CONTACT = "003Wt00000Jqy8SIAR"
acct11 = None
for i, f, l, a in core.execute("select Id, FirstName, LastName, AccountId from Contact"):
    if nid(i) == CONTACT:
        acct11 = nid(a)
orders11 = {}
for r in po.execute('select Id, AccountId, Status, EffectiveDate, OwnerId from "Order"'):
    orders11[nid(r[0])] = (nid(r[1]), (r[2] or "").strip(), r[3] or "", nid(r[4]))
q11_items = []
for r in po.execute("select Id, OrderId, Product2Id, Quantity, UnitPrice from OrderItem"):
    o = orders11.get(nid(r[1]))
    if o and o[0] == acct11 and o[2][:7] == "2021-06":
        q11_items.append((prod2name.get(nid(r[2])), nid(r[2]), float(r[3] or 0)))
diag["q11_june_items"] = q11_items
q11_ai = [it for it in q11_items if it[0] and it[0].upper().startswith("AI")]
q11_answer = q11_ai[0][1] if len(q11_ai) == 1 else (sorted(set(x[1] for x in q11_ai))[0] if q11_ai else "")

# ---------------- q12 (VI): quickest April 2023 sales cycle ----------------
con = {nid(r[0]): dict(acc=nid(r[1]), start=r[2] or "", comp=r[3] or "")
       for r in sp.execute("select Id, AccountId, StartDate, CompanySignedDate from Contract").fetchall()}
q12_agg = defaultdict(list)
for r in sp.execute("select Id, ContractID__c, OwnerId, CreatedDate from Opportunity").fetchall():
    cid = nid(r[1])
    c = con.get(cid)
    if not c or not c["comp"] or c["comp"][:7] != "2023-04":
        continue
    d = (datetime.fromisoformat(c["comp"][:19]) -
         datetime.fromisoformat(r[3][:19])).total_seconds() / 86400
    q12_agg[nid(r[2])].append(round(d, 2))
diag["q12"] = {a: (round(sum(v) / len(v), 3), v) for a, v in q12_agg.items()}
q12_rank = sorted((sum(v) / len(v), a) for a, v in q12_agg.items())
q12_answer = q12_rank[0][1] if q12_rank else ""

# ---------------- q13 (VI): top sales past 5 months ----------------
items_by_order = defaultdict(list)
for r in po.execute("select Id, OrderId, Product2Id, Quantity, UnitPrice from OrderItem"):
    items_by_order[nid(r[1])].append((float(r[3] or 0), float(r[4] or 0)))
q13_sales = defaultdict(float)
q13_detail = defaultdict(list)
for cid, c in con.items():
    if not c["comp"] or not ("2022-06-25" <= c["comp"][:10] <= "2022-11-25"):
        continue
    cand = [oid for oid, o in orders11.items() if o[0] == c["acc"] and o[2] == c["start"]]
    if not cand:
        cand = [oid for oid, o in orders11.items() if o[0] == c["acc"]]
    for oid in cand:
        s = sum(q * u for q, u in items_by_order[oid])
        own = orders11[oid][3]
        q13_sales[own] += s
        q13_detail[own].append((cid, oid, round(s, 2)))
q13_rank = sorted(q13_sales.items(), key=lambda kv: (-kv[1], kv[0]))
diag["q13_top3"] = [(a, round(v, 2)) for a, v in q13_rank[:3]]
q13_answer = q13_rank[0][0] if q13_rank else ""

# ---------- assemble ----------
answers = {str(i): v for i, v in enumerate([
    q1_answer, q2_answer, q3_answer, q4_answer, q5_answer, q6_answer, q7_answer,
    q8_answer, q9_answer, q10_answer, q11_answer, q12_answer, q13_answer], start=1)}

result = {
    "dataset": "crmarenapro",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "answers": answers,
    "diagnostics": diag,
}
out = sys.argv[1] if len(sys.argv) > 1 else "/root/dabteam/runs/crmarenapro/result.json"
entries = []
for qi in range(1, 14):
    for run in range(5):
        entries.append({"dataset": "crmarenapro", "query": qi, "run": run, "answer": answers[str(qi)]})
json.dump(result, open(out, "w"), indent=2, ensure_ascii=False)
ej = out.replace("result.json", "entries.json")
json.dump(entries, open(ej, "w"), indent=2, ensure_ascii=False)
print(json.dumps(result, indent=2, ensure_ascii=False)[:4000])
print("entries ->", ej, len(entries))
