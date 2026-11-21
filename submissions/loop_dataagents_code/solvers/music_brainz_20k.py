#!/usr/bin/env python3
"""music_brainz_20k q1-q3 deterministic solver — implements frozen/music_brainz_20k_readings.md
(preregistered 2026-11-09T07:25Z). No LLM calls.
Stores: tracks.db (dabdata copy) + sales.duckdb (official repo copy; dabdata mirror lacks it).
"""
import json, re, sys, time, unicodedata
from collections import defaultdict

import duckdb
from rapidfuzz import fuzz, process as rf_process

TRACKS = "/root/dabdata/query_music_brainz_20k/query_dataset/tracks.db"
SALES = "/root/work/DataAgentBench/query_music_brainz_20k/query_dataset/sales.duckdb"

MISSING_ARTIST = {None, "", "[unknown]", "unknown", "none", "null", "unk."}

def norm(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    # \w keeps unicode letters/digits (Cyrillic artists must not vanish into "missing")
    return re.sub(r"[^\w]|_", "", s.lower())

PREFIX_RE = re.compile(r"^\s*\d{1,4}[-_.\s]+")
PAREN_RE = re.compile(r"\s*\([^)]*\)\s*")

def clean_title(title, artist, albums_set):
    """Return (clean_title, artist_from_title). Iterative rule set from the frozen file."""
    t = (title or "").strip()
    for _ in range(3):
        t2 = PREFIX_RE.sub("", t)
        t2 = PAREN_RE.sub(" ", t2)
        t2 = t2.strip(" -–—")
        if " - " in t2:
            left, right = [x.strip() for x in t2.split(" - ", 1)]
            ln, rn = norm(left), norm(right)
            an = norm(artist) if artist not in MISSING_ARTIST else ""
            left_is_artist = an and fuzz.ratio(ln, an) >= 85
            left_missing_artist = artist in MISSING_ARTIST
            if left_is_artist or (left_missing_artist and ln and ln not in albums_set):
                t2 = right
            else:
                # right side looks like an album variant?
                rn_album = any(fuzz.partial_ratio(rn, al) >= 85 for al in albums_set if al)
                if rn_album or (not rn):
                    t2 = left
        if t2 == t:
            break
        t = t2
    return t.strip()

diag = {}
con = duckdb.connect(TRACKS, read_only=True)
rows = con.execute("select track_id, source_id, title, artist, album, year from tracks").fetchall()
con.close()
albums_norm = {norm(a) for (_, _, _, _, a, _) in rows if a}

recs = []
for tid, sid, title, artist, album, year in rows:
    ct = clean_title(title, artist, albums_norm)
    anorm = "" if artist in MISSING_ARTIST else norm(artist or "")
    recs.append({
        "track_id": tid, "title_clean": ct, "title_norm": norm(ct),
        "artist": artist or "", "artist_norm": anorm,
        "album_norm": norm(album) if album else "",
        "year": (year or "").strip().strip("'")[-2:],
    })
diag["tracks"] = len(recs)

# ---------- union-find clustering (blocked by first 2 alnum of title norm) ----------
parent = list(range(len(recs)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[max(ra, rb)] = min(ra, rb)

PLACEHOLDER_TITLES = {"untitled", "unknown", "notitle", "noname"}  # rev.2: not real titles

blocks = defaultdict(list)
for i, r in enumerate(recs):
    tn = r["title_norm"]
    if tn and tn not in PLACEHOLDER_TITLES:
        blocks[tn[:2]].append(i)
        blocks["3:" + tn[:3]].append(i)
    if r["artist_norm"]:
        blocks["A:" + r["artist_norm"][:2]].append(i)
        blocks["A3:" + r["artist_norm"][:3]].append(i)

pair_checks = 0
merged = 0
for key, idxs in blocks.items():
    n = len(idxs)
    if n > 800:  # guard: huge blocks skipped, logged
        diag.setdefault("oversize_blocks", []).append((key, n))
        continue
    for ai in range(n):
        i = idxs[ai]
        ri = recs[i]
        for bi in range(ai + 1, n):
            j = idxs[bi]
            rj = recs[j]
            ti, tj = ri["title_norm"], rj["title_norm"]
            if not ti or not tj:
                continue
            pair_checks += 1
            short, long_ = (ti, tj) if len(ti) <= len(tj) else (tj, ti)
            # fragmentation guard (rev.3): short norms match only exactly;
            # generic fragments ("Concerto", "Mein") must not absorb real titles
            if len(short) < 10:
                if ti != tj:
                    continue
                tsim = 100.0
            else:
                tsim = max(fuzz.ratio(ti, tj), fuzz.partial_ratio(short, long_))
            if tsim < 90:
                continue
            a_i, a_j = ri["artist_norm"], rj["artist_norm"]
            if a_i and a_j:
                if fuzz.ratio(a_i, a_j) < 85:
                    continue
            else:
                # rev.3: tightened — loose year+partial paths merged unrelated
                # classical works; album support or exact title + year required
                al_i, al_j = ri["album_norm"], rj["album_norm"]
                ok = False
                if al_i and al_j and fuzz.ratio(al_i, al_j) >= 80:
                    ok = True
                elif ti == tj and ri["year"] and rj["year"] and ri["year"] == rj["year"]:
                    ok = True
                if not ok:
                    continue
            if find(i) != find(j):
                union(i, j)
                merged += 1
diag["pair_checks"] = pair_checks
diag["union_ops"] = merged

clusters = defaultdict(list)
for i in range(len(recs)):
    clusters[find(i)].append(i)
diag["clusters"] = len(clusters)

# cluster representative title = mode of cleaned titles
def cluster_title(idxs):
    cnt = defaultdict(int)
    for i in idxs:
        cnt[recs[i]["title_clean"]] += 1
    best = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))
    return best[0][0]

# ---------- sales ----------
sc = duckdb.connect(SALES, read_only=True)
sales = sc.execute("select track_id, country, store, revenue_usd from sales").fetchall()
sc.close()
diag["sales"] = len(sales)
track2cluster = {}
for i, r in enumerate(recs):
    track2cluster[r["track_id"]] = find(i)

rev_all = defaultdict(float)                 # cluster -> total
rev_q1 = defaultdict(float)                  # cluster -> apple music canada
rev_q2 = defaultdict(lambda: defaultdict(float))  # cluster -> store -> total
for tid, country, store, rev in sales:
    c = track2cluster.get(tid)
    if c is None:
        continue
    rev_all[c] += rev or 0.0
    rev_q2[c][store] += rev or 0.0
    if store == "Apple Music" and country == "Canada":
        rev_q1[c] += rev or 0.0

# ---------------- q1 ----------------
q1_clusters = [c for c in clusters
               if any(fuzz.partial_ratio(recs[i]["title_norm"], "getmebodied") >= 90 for i in clusters[c])
               and any((recs[i]["artist_norm"] and fuzz.ratio(recs[i]["artist_norm"], "beyonce") >= 90) for i in clusters[c])]
diag["q1_clusters"] = [(c, [recs[i]["track_id"] for i in clusters[c]]) for c in q1_clusters]
q1_val = sum(rev_q1[c] for c in q1_clusters)
q1_answer = f"{round(q1_val, 2)}"

# ---------------- q2 ----------------
q2_clusters = [c for c in clusters
               if any(fuzz.partial_ratio(recs[i]["title_norm"], "streethype") >= 90 for i in clusters[c])
               and any((recs[i]["artist_norm"] and fuzz.ratio(recs[i]["artist_norm"], "brucqemaginnis") >= 85) for i in clusters[c])]
diag["q2_clusters"] = [(c, [recs[i]["track_id"] for i in clusters[c]]) for c in q2_clusters]
store_tot = defaultdict(float)
for c in q2_clusters:
    for st, v in rev_q2[c].items():
        store_tot[st] += v
q2_answer = sorted(store_tot.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] if store_tot else ""
diag["q2_store_totals"] = dict(store_tot)

# ---------------- q3 ----------------
top = sorted(rev_all.items(), key=lambda kv: (-kv[1], cluster_title(clusters[kv[0]])))[:5]
diag["q3_top5"] = [(cluster_title(clusters[c]), round(v, 2), len(clusters[c])) for c, v in top]
q3_answer = cluster_title(clusters[top[0][0]])

result = {
    "dataset": "music_brainz_20k",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "q1_answer": q1_answer, "q2_answer": q2_answer, "q3_answer": q3_answer,
    "diagnostics": diag,
}
out = sys.argv[1] if len(sys.argv) > 1 else "/root/dabteam/runs/music_brainz_20k/result.json"
json.dump(result, open(out, "w"), indent=2, ensure_ascii=False)
print(json.dumps(result, indent=2, ensure_ascii=False))
