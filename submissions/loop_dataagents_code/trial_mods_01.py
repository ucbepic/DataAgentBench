#!/usr/bin/env python3
"""Build harness trial modules for dab-agent-01's six datasets (option (a) of the
D4 traces-layout request). Each module's steps run the dataset's deterministic
solver in a fresh temporary output directory and extract that query's answer.
No answer literals appear in code or steps.
"""
import json, os, types

REPO = "/root/work/DataAgentBench"
AGENT = "dab-agent-01"

# dataset -> (solver path, legacy shared-output path [unused; trials use a fresh temp dir], answer expr per query, derivation per query)
CONF = {
    "DEPS_DEV_V1": {
        "solver": "/root/dabteam/solvers/deps_dev_v1.py",
        "out": "/root/dabteam/runs/DEPS_DEV_V1/result.json",
        "expr": lambda q: f'res["q{q}_answer"]',
        "deriv": {
            "1": "latest release per NPM package by VersionInfo.Ordinal; GitHub stars parsed from project_info text; top-5 lines 'N. pkg (ver) - stars [repo]'",
            "2": "[VI] project-level MIT licence (any release) qualifies; rank projects by forks parsed from project_info; top-5 'N. repo - forks'",
        },
    },
    "GITHUB_REPOS": {
        "solver": "/root/dabteam/solvers/github_repos.py",
        "out": "/root/dabteam/runs/GITHUB_REPOS/result.json",
        "expr": lambda q: f'res["q{q}_answer"]',
        "deriv": {
            "1": "[R003/D3] README corpus = files join contents on blob id, lower(path) LIKE '%readme.md'; 'do not use Python' = language_description lacks substring 'Python'; proportion = copyright-bearing distinct blobs / distinct blobs; CSV 2 lines",
            "2": "most-copied non-binary .swift blob (repo_data_description copy count), repos resolved via files; exact-token Swift membership; 'repo_name' header + repo",
            "3": "Apache-2.0 licences + exact-token Shell membership; commit messages non-null, <1000 chars, not starting merge/update/test; 'num_messages' header + count",
            "4": "commits per repo; main language = max byte share, exact-token; exclude Python-main; top-5 CSV 'repo_name,num_commits'",
        },
    },
    "music_brainz_20k": {
        "solver": "/root/dabteam/solvers/music_brainz_20k.py",
        "out": "/root/dabteam/runs/music_brainz_20k/result.json",
        "expr": lambda q: f'res["q{q}_answer"]',
        "deriv": {
            "1": "entity resolution of duplicate track copies (title normalisation + fuzzy match, artist/album support), then total revenue aggregation",
            "2": "same resolution; revenue share per sales channel/store, argmax",
            "3": "same resolution; argmax track title by revenue",
        },
    },
    "stockindex": {
        "solver": "/root/dabteam/solvers/stockindex.py",
        "out": "/root/dabteam/runs/stockindex/result.json",
        "expr": lambda q: f'res["q{q}_answer"]',
        "deriv": {
            "1": "Asia indices per index_info; intraday volatility (High-Low)/Open averaged over rows since 2020-01-01; argmax; single line with exchange full name, country, 4-dp volatility",
            "2": "North America indices; up day Close>Open, down Close<Open, year 2018; indices with up>down; 'SYM (exchange, country) - up vs down days'",
            "3": "monthly DCA $1 (first trading day of each month from 2000-01 or first available), value at last CloseUSD; top-5 'N. SYM (country) - return% over N monthly investments'",
        },
    },
    "stockmarket": {
        "solver": "/root/dabteam/solvers/stockmarket.py",
        "out": "/root/dabteam/runs/stockmarket/result.json",
        "expr": lambda q: f'res["q{q}_answer"]',
        "deriv": {
            "1": "company name parsed from Company Description prefix (verb-boundary table); The RealReal symbol; max Adj Close in 2020, 2-dp",
            "2": "ETF='Y' and Listing Exchange='P'; any 2019..2015 Adj Close > 200; lines 'SYM: name' + total line",
            "3": "Financial Status in D/E/H and Market Category in Q/G/S; 2008 non-null Volume mean desc; 'name (SYM): average daily volume x.xx over N trading days'",
            "4": "question-defined up/down days = Close vs Open (R015, 2026-11-10; supersedes [VI] close-to-close); ETF='N', NYSE; year 2017; rank by (up-down) desc, symbol asc; 'N. name (SYM) - up up days, down down days'",
            "5": "Market Category 'S'; 2019 days with (High-Low)/Low > 0.20; rank days desc, symbol asc; 'N. name (SYM) - D qualifying days'",
        },
    },
    "crmarenapro": {
        "solver": "/root/dabteam/solvers/crmarenapro.py",
        "out": "/root/dabteam/runs/crmarenapro/result.json",
        "expr": lambda q: f'res["answers"]["{q}"]',
        "deriv": {
            "1": "BANT parse of the lead's voice-call transcript; failing factor line",
            "2": "quote lines vs Volume-Based Discounts tiers (qty>=20/15%, >=10/10%, >=5/5%); precedence qty-limit > discount > bundle; article id via runtime title lookup, '#' stripped",
            "3": "latest Task by ActivityDate mapped to stage labels via keyword table",
            "4": "cases linked through orderitemid to the product; created-month histogram in the policy window; peak month name",
            "5": "same product link; issue id counts in window; argmax",
            "6": "quote lines vs Product Quantity Limits per-order table parsed from the article body; article id via runtime title lookup, '#' stripped",
            "7": "case email chain (parent/related join, nid-normalised); recommended package mapped to its governing KAV article; no catalogue product / purchase record exists; governing article id returned",
            "8": "casehistory Owner Assignment consecutive-pair transfers in window, credited to the newvalue-side agent; argmin over involved agents",
            "9": "closed cases in window; close-created duration by account ShippingState; min mean",
            "10": "single-assignment (non-transferred) closed cases in window; mean handle hours; agents handling >1; argmin",
            "11": "contact->account orders in month; items whose product name starts 'AI'; product id",
            "12": "[VI] contracts by CompanySignedDate month; sales cycle = contract signed - opportunity created; mean by opportunity owner; argmin",
            "13": "[VI] contracts in window linked to orders (account + EffectiveDate==StartDate); sum Quantity*UnitPrice by order owner; argmax",
        },
    },
}

STEP_TEMPLATE = """import json, os, shutil, subprocess, sys, tempfile
SOLVER = {solver!r}
# Each trial computes the answer in its own fresh output dir: no shared or
# prior-run result file is read (rubric 2.1 treats those as off-limits).
TD = tempfile.mkdtemp(prefix="dab_trial_")
OUT = os.path.join(TD, "result.json")
p = subprocess.run([sys.executable, SOLVER, OUT], capture_output=True, text=True)
print("solver rc:", p.returncode)
print(p.stdout)
if p.returncode != 0:
    print(p.stderr)
res = json.load(open(OUT))
val = {expr}
print(val)
ANSWER = val
shutil.rmtree(TD, ignore_errors=True)"""


def load_query_text(ds, q):
    p = f"{REPO}/query_{ds}/query{q}/query.json"
    try:
        return json.load(open(p))
    except Exception:
        return open(p).read().strip()


def build(ds):
    c = CONF[ds]
    qs = sorted(c["deriv"], key=int)
    texts = {q: load_query_text(ds, q) for q in qs}
    steps = {q: [("run_solver_and_extract", STEP_TEMPLATE.format(
        solver=c["solver"], out=c["out"], expr=c["expr"](q)))] for q in qs}
    mod = types.SimpleNamespace(
        DATASET=ds, AGENT=AGENT, QUERY_TEXTS=texts, STEPS=steps,
        DERIVATION=c["deriv"],
    )
    return mod
