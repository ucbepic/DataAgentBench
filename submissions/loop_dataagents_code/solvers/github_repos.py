#!/usr/bin/env python3
"""GITHUB_REPOS q1-q4 deterministic solver — implements frozen/GITHUB_REPOS_readings.md
(preregistered 2026-11-09, amendment registered pre-answer 06:55Z). No LLM calls.
Sanctioned stores: repo_metadata.db (sqlite: repos/languages/licenses),
repo_artifacts.db (duckdb: files/contents/commits).
Single pass over the 3.3M-row languages table (no usable index there).
"""
import json, re, sqlite3, sys, time
import duckdb

META = "/root/dabdata/query_GITHUB_REPOS/query_dataset/repo_metadata.db"
ART = "/root/dabdata/query_GITHUB_REPOS/query_dataset/repo_artifacts.db"

diag = {}

# token parser: language names are proper-cased possibly multi-word ("Vim script",
# "Jupyter Notebook"); filler before "(" is lowercase so start-uppercase anchor works.
LANG_TOK = re.compile(r"([A-Z][A-Za-z0-9+#.\-]*(?:[ ][A-Za-z0-9+#.\-]+)*) \(([\d,]+) bytes\)")

def parse_langs(desc):
    toks = {}
    for name, b in LANG_TOK.findall(desc):
        toks[name] = toks.get(name, 0) + int(b.replace(",", ""))
    return toks

meta = sqlite3.connect(f"file:{META}?mode=ro", uri=True)
art = duckdb.connect(ART, read_only=True)

# ---------- inputs that define which languages rows we need ----------
readme_blobs = art.execute(
    "select id, sample_repo_name, contains(lower(content), 'copyright') cr"
    " from contents where sample_path = 'README.md'").fetchall()
rb_repos = {r[1] for r in readme_blobs}

sw = art.execute("""
  select c.id, c.sample_repo_name, c.repo_data_description
  from contents c
  where c.id in (select distinct id from files where path like '%.swift')
    and contains(lower(c.repo_data_description), 'non-binary')
""").fetchall()
COPY = re.compile(r"(\d+)\s+times")
best, ties = None, []
for rid, repo, desc in sw:
    m = COPY.search(desc)
    if not m:
        continue
    c = int(m.group(1))
    if best is None or c > best[0]:
        best, ties = (c, rid, repo), [rid]
    elif c == best[0]:
        ties.append(rid)
diag["q2_nonbinary_swift_blobs"] = len(sw)
diag["q2_top_copies"] = best[0] if best else None
diag["q2_top_ties"] = len(ties)
q2_repos = ({r[0] for r in art.execute(
    "select distinct repo_name from files where id = ?", [best[1]]).fetchall()}
    if best else set())

apache = {r[0] for r in meta.execute(
    "select repo_name from licenses where lower(trim(license)) = 'apache-2.0'")}
diag["q3_apache_repos"] = len(apache)

commit_counts = art.execute(
    "select repo_name, count(*) c from commits group by repo_name").fetchall()
commits_repos = {r for r, _ in commit_counts}
diag["q4_repos_in_commits"] = len(commits_repos)

# ---------- ONE pass over languages ----------
need = rb_repos | q2_repos | commits_repos | apache
langs = {}
for name, desc in meta.execute("select repo_name, language_description from languages"):
    if name in need:
        langs[name] = parse_langs(desc)
diag["langs_rows_parsed"] = len(langs)

# ---------------- q1 (amendment 3, D3 2026-11-09: inherited passing reading) ----------------
# Reading inherited from the prior team's passing pipeline (D3 adjudication): the
# README corpus is files-join-contents on blob id with lower(path) LIKE '%readme.md';
# "do not use Python" is a substring test on language_description.
joined = art.execute("""
  select f.id, f.repo_name, contains(lower(c.content),'copyright') cr
  from files f join contents c on f.id = c.id
  where lower(f.path) like '%readme.md'
""").fetchall()
jrepos = sorted({r[1] for r in joined})
ph = ",".join("?" * len(jrepos))
uses_py = {r[0] for r in meta.execute(
    f"select repo_name from languages where repo_name in ({ph}) and language_description like '%Python%'",
    jrepos)}
sel1 = [r for r in joined if r[1] not in uses_py]
ids1 = {r[0] for r in sel1}
n_copy1 = sum(1 for r in sel1 if r[2])
diag["q1_joined_readme_blobs"] = len(joined)
diag["q1_distinct_readme_blob_ids"] = len(ids1)
diag["q1_ids_with_copyright"] = n_copy1
q1_answer = (f"total_readmes,copyright_readmes,proportion\n"
             f"{len(ids1)},{n_copy1},{n_copy1/len(ids1)!r}" if ids1 else
             "total_readmes,copyright_readmes,proportion\n0,0,0")

# ---------------- q2 ----------------
swift_ok = {r for r in q2_repos if r in langs and "Swift" in langs[r]}
diag["q2_blob_repos"] = sorted(q2_repos)
diag["q2_blob_repos_with_swift"] = sorted(swift_ok)
q2_repo = None
if best:
    pick = (swift_ok or q2_repos)
    q2_repo = sorted(pick)[0] if len(pick) >= 1 else None
q2_answer = f"repo_name\n{q2_repo}" if q2_repo else "repo_name"

# ---------------- q3 ----------------
shell_repos = {r for r in apache if r in langs and "Shell" in langs[r]}
diag["q3_shell_apache_repos"] = len(shell_repos)
q3_rows = art.execute("""
  select count(*) from commits
  where repo_name in (select unnest(?::varchar[]))
    and message is not null and message != ''
    and length(message) < 1000
    and not (starts_with(lower(message), 'merge') or starts_with(lower(message), 'update')
             or starts_with(lower(message), 'test'))
""", [sorted(shell_repos)]).fetchone()[0] if shell_repos else 0
diag["q3_qualifying_messages"] = q3_rows
q3_answer = f"num_messages\n{q3_rows}"

# ---------------- q4 ----------------
diag["q4_repos_with_langs_row"] = sum(1 for r in commits_repos if r in langs)
ranked = []
for repo, c in commit_counts:
    toks = langs.get(repo)
    if not toks:
        continue
    main = max(toks.items(), key=lambda kv: (kv[1], [-ord(ch) for ch in kv[0]]))[0]
    if main != "Python":
        ranked.append((c, repo))
ranked.sort(key=lambda t: (-t[0], t[1]))
q4_top = ranked[:5]
diag["q4_top_with_ties_context"] = ranked[:8]
q4_answer = ("repo_name,num_commits\n" +
             "\n".join(f"{repo},{c}" for c, repo in q4_top))

result = {
    "dataset": "GITHUB_REPOS",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "q1_answer": q1_answer, "q2_answer": q2_answer,
    "q3_answer": q3_answer, "q4_answer": q4_answer,
    "q4_top": q4_top,
    "diagnostics": diag,
}
out = sys.argv[1] if len(sys.argv) > 1 else "/root/dabteam/runs/GITHUB_REPOS/result.json"
json.dump(result, open(out, "w"), indent=2, ensure_ascii=False)
answers = {"1": q1_answer, "2": q2_answer, "3": q3_answer, "4": q4_answer}
entries = [{"dataset": "GITHUB_REPOS", "query": qi, "run": run, "answer": answers[qi]}
           for qi in answers for run in range(5)]
ej = out.replace("result.json", "entries.json")
json.dump(entries, open(ej, "w"), indent=2, ensure_ascii=False)
print(json.dumps(result, indent=2, ensure_ascii=False))
print("entries ->", ej, len(entries))
