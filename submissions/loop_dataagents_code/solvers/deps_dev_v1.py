#!/usr/bin/env python3
"""DEPS_DEV_V1 q1/q2 deterministic solver — implements frozen/DEPS_DEV_V1_readings.md
(preregistered 2026-11-09). No LLM calls. Sanctioned stores only:
  package_query.db (sqlite, packageinfo) + project_query.db (duckdb, project_info/project_packageversion)
Outputs answers (leaderboard entry list) + diagnostics for the trace file.
"""
import json, re, sqlite3, sys, time
from collections import defaultdict

import duckdb

PK = "/root/dabdata/query_DEPS_DEV_V1/query_dataset/package_query.db"
PJ = "/root/dabdata/query_DEPS_DEV_V1/query_dataset/project_query.db"

t0 = time.time()
diag = {}

# ---------- load packageinfo (sqlite) ----------
con = sqlite3.connect(f"file:{PK}?mode=ro", uri=True)
pkg_rows = con.execute(
    "select System, Name, Version, VersionInfo from packageinfo"
).fetchall()
con.close()
diag["packageinfo_rows"] = len(pkg_rows)
diag["systems"] = sorted({r[0] for r in pkg_rows})

# per (Name): latest release row = max Ordinal among IsRelease=true
latest = {}          # Name -> (ordinal, version)
release_any = set()  # Names with >=1 IsRelease=true row
bad_versioninfo = 0
for system, name, version, vinfo in pkg_rows:
    try:
        vi = json.loads(vinfo)
        is_rel = bool(vi.get("IsRelease"))
        ordinal = vi.get("Ordinal")
    except Exception:
        bad_versioninfo += 1
        continue
    if is_rel:
        release_any.add(name)
        cur = latest.get(name)
        if cur is None or (ordinal is not None and ordinal > cur[0]):
            latest[name] = (ordinal, version)
diag["distinct_names"] = len(latest)
diag["names_with_any_release"] = len(release_any)
diag["bad_versioninfo_rows"] = bad_versioninfo

# ---------- load project side (duckdb) ----------
dj = duckdb.connect(PJ, read_only=True)
ppv = dj.execute(
    "select System, Name, Version, ProjectName from project_packageversion"
).fetchall()
pinfo = dj.execute("select Project_Information, Licenses from project_info").fetchall()
dj.close()
diag["project_packageversion_rows"] = len(ppv)
diag["project_info_rows"] = len(pinfo)

# map (System,Name,Version) -> set(ProjectName)
pkg2proj = defaultdict(set)
for system, name, version, pname in ppv:
    pkg2proj[(system, name, version)].add(pname)

# parse project_info: join key = owner/repo token matched to ppv.ProjectName
# (exact match; fallbacks logged). Metrics via dual patterns with consistency check.
URL_RE = re.compile(r"https?://\S+")
TOK_RE = re.compile(
    r"(?:^|[\s,(])([A-Za-z0-9_.\-]{1,60}/[A-Za-z0-9_.\-#@%]{1,80})(?=[\s,).;:!?]|$)"
)
S_PATS = [re.compile(r"stars? count of ([\d,]+)"),
          re.compile(r"([\d,]+)\s+stars?"),
          re.compile(r"starred by ([\d,]+) users")]
F_PATS = [re.compile(r"forks? count of ([\d,]+)"),
          re.compile(r"([\d,]+)\s+forks?"),
          re.compile(r"forked ([\d,]+) times")]

def _num(s):
    return int(s.replace(",", ""))

def _metrics(info):
    sv, fv = set(), set()
    for p in S_PATS:
        sv |= {_num(m.group(1)) for m in p.finditer(info)}
    for p in F_PATS:
        fv |= {_num(m.group(1)) for m in p.finditer(info)}
    return sv, fv

projects = {}  # ProjectName -> dict(licenses, stars, forks)
pn_lower = {p.lower(): p for p in {r[3] for r in ppv}}
name_map_log = {"exact": 0, "ci": 0, "prefix": 0, "org_word": 0, "unresolved": [], "metric_conflict": []}
for info, lic in pinfo:
    text = URL_RE.sub(" ", info)
    toks = [t.rstrip(".,;:") for t in TOK_RE.findall(text)]
    pname = next((t for t in toks if t in pn_lower), None)
    if pname is None:
        ci = next((pn_lower[t.lower()] for t in toks if t.lower() in pn_lower), None)
        if ci is not None:
            pname, name_map_log["ci"] = ci, name_map_log["ci"] + 1
    if pname is None:  # unique prefix of a known ProjectName (e.g. truncated repo)
        cands = {p for t in toks for p in pn_lower.values() if p.startswith(t) and t.count("/") == 1}
        if len(cands) == 1:
            pname = next(iter(cands))
            name_map_log["prefix"] += 1
            name_map_log.setdefault("prefix_mapped", []).append((sorted(cands)[0], toks))
    if pname is None:  # "<org> ... <repo-word>" composition
        words = set(re.findall(r"[A-Za-z0-9_.\-]{3,}", text))
        cands = {p for p in pn_lower.values()
                 if p.split("/")[0] in words and p.split("/", 1)[1] in words}
        if len(cands) == 1:
            pname = next(iter(cands))
            name_map_log["org_word"] += 1
    if pname is None:
        name_map_log["unresolved"].append(text[:120])
        continue
    name_map_log["exact"] += 1
    sv, fv = _metrics(info)
    if len(sv) != 1 or len(fv) != 1:
        name_map_log["metric_conflict"].append((pname, sorted(sv), sorted(fv), text[:140]))
        continue
    try:
        licenses = json.loads(lic) if lic else []
    except Exception:
        licenses = []
    if pname in projects:
        name_map_log.setdefault("dup_project_rows", []).append(pname)
        continue
    projects[pname] = {"licenses": licenses, "stars": sv.pop(), "forks": fv.pop()}
diag["projects_with_metrics"] = len(projects)
diag["name_map"] = {k: v for k, v in name_map_log.items() if k != "unresolved"} | {
    "unresolved_count": len(name_map_log["unresolved"])}

# ---------------- q1 ----------------
# latest release per package -> project(s) -> stars; top5 package-versions
q1_rows = []
multi_proj = 0
for name, (ordinal, version) in latest.items():
    targets = pkg2proj.get(("NPM", name, version))
    if not targets:
        continue
    if len(targets) > 1:
        multi_proj += 1
    # deterministic: if a package version links multiple projects, take the one
    # with max stars (then name asc) and record the ambiguity count
    cands = []
    for tp in sorted(targets):
        p = projects.get(tp)
        if p:
            cands.append((p["stars"], p["forks"], tp))
    if not cands:
        continue
    cands.sort(key=lambda c: (-c[0], c[2]))
    stars, forks, tp = cands[0]
    q1_rows.append({"name": name, "version": version, "ordinal": ordinal,
                    "stars": stars, "forks": forks, "project": tp})
diag["q1_linked_latest_packages"] = len(q1_rows)
diag["q1_multi_project_links"] = multi_proj
q1_rows.sort(key=lambda r: (-r["stars"], -(r["ordinal"] or -1), r["name"]))
q1_top = q1_rows[:5]
q1_answer = "\n".join(
    f"{i+1}. {r['name']} ({r['version']}) - {r['stars']} GitHub stars [{r['project']}]"
    for i, r in enumerate(q1_top)
)

# ---------------- q2 ----------------
# project-level Licenses == ["MIT"]; package any-release; link via any version row
mit_projects = {p for p, d in projects.items() if d["licenses"] == ["MIT"]}
diag["q2_mit_projects"] = len(mit_projects)
q2_proj_stars = defaultdict(set)  # project -> qualifying package names (for audit)
for (system, name, version), targets in pkg2proj.items():
    if system != "NPM" or name not in release_any:
        continue
    for tp in targets & mit_projects:
        q2_proj_stars[tp].add(name)
q2_rows = [{"project": tp, "forks": projects[tp]["forks"],
            "n_pkgs": len(names)} for tp, names in q2_proj_stars.items()]
diag["q2_candidate_projects"] = len(q2_rows)
q2_rows.sort(key=lambda r: (-r["forks"], r["project"]))
q2_top = q2_rows[:5]
q2_answer = "\n".join(
    f"{i+1}. {r['project']} - {r['forks']} GitHub forks"
    for i, r in enumerate(q2_top)
)

result = {
    "dataset": "DEPS_DEV_V1",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "q1_answer": q1_answer,
    "q2_answer": q2_answer,
    "q1_top": q1_top,
    "q2_top": q2_top,
    "diagnostics": diag,
}
out = sys.argv[1] if len(sys.argv) > 1 else "/root/dabteam/runs/DEPS_DEV_V1/result.json"
json.dump(result, open(out, "w"), indent=2, ensure_ascii=False)
print(json.dumps(result, indent=2, ensure_ascii=False))
