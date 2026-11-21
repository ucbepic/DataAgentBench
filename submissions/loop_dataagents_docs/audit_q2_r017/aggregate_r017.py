#!/usr/bin/env python3
"""R017 aggregation: three clean single-pass annotators, per-article majority.
Pre-registered in audit_q2_r017/PROTOCOL.md. Reads only the frozen input and the
three raw pass files; R016 labels are used only as the fallback for under-voted
articles and as the comparison baseline.
"""
import json, hashlib, collections, os, sqlite3

D = "/root/dabteam/audit_q2_r017"
ITEMS_SHA = "b63fb33a363a6a3197e3cd02e688c39472ee1d98e0def220590689dcb5cd94a5"
LABELS = ("World", "Sports", "Business", "Science/Technology")


def load(path):
    raw = open(path).read().lstrip()
    rows = json.loads(raw) if raw.startswith("[") else [
        json.loads(l) for l in raw.splitlines() if l.strip()]
    out = {}
    for i, r in enumerate(rows, 1):
        aid = str(r.get("article_id", r.get("id", "")))
        if not aid:
            raise SystemExit(f"{path}:{i}: missing article_id")
        if aid in out:
            raise SystemExit(f"{path}:{i}: duplicate {aid}")
        if r.get("label") not in LABELS:
            raise SystemExit(f"{path}:{i}: bad label {r.get('label')!r}")
        out[aid] = r["label"]
    return out


def main():
    raw = open(f"{D}/items.json", "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    items = json.loads(raw)
    ids = {str(r["article_id"]) for r in items}
    assert sha == ITEMS_SHA, f"input hash {sha} != frozen {ITEMS_SHA}"
    assert len(ids) == len(items) == 111

    passes = {k: load(f"{D}/pass{k}.json") for k in "ABC"}
    for k, v in passes.items():
        assert set(v) == ids, f"pass{k}: ids differ (+{len(set(v)-ids)} -{len(ids-set(v))})"

    # R016 baseline (frozen majority + R016 consensus override)
    base = {str(r["article_id"]): r["label"] for r in
            json.load(open("/root/dabteam/runs/agnews_labels/majority_labels.json"))}
    ov = json.load(open("/root/dabteam/runs/agnews_labels/q2_audit_override.json"))
    base.update({k: v for k, v in ov.items() if v in LABELS})

    majority, votes, fallback = {}, {}, []
    for aid in sorted(ids):
        c = collections.Counter(passes[k][aid] for k in "ABC")
        top, n = c.most_common(1)[0]
        if n < 2:
            majority[aid] = base[aid]
            fallback.append(aid)
        else:
            majority[aid] = top
        votes[aid] = dict(c)

    changes = sorted([a for a in ids if majority[a] != base[a]], key=int)
    n_sci = sum(1 for a in ids if majority[a] == "Science/Technology")
    n_old = sum(1 for a in ids if base[a] == "Science/Technology")
    print(f"input sha {sha} OK; passes 111/111 each")
    print(f"fallback articles (<2 valid votes): {fallback}")
    print(f"label changes vs R016: {len(changes)}")
    for a in changes:
        print(f"  {a}: {base[a]} -> {majority[a]} votes={votes[a]}")
    print(f"q2 S&T: {n_old} -> {n_sci} / 111 = {n_sci/111:.4f}")
    print("PASS" if n_sci == 16 else "FAIL (target 16)")

    # informational collateral (R017 is q2-only; not applied elsewhere)
    con = sqlite3.connect("file:/root/dabdata/query_agnews/query_dataset/metadata.db?mode=ro", uri=True)
    meta = {str(a): (rg, pd) for a, rg, pd in
            con.execute("select article_id, region, publication_date from article_metadata")}
    con.close()
    B = [a for a, (rg, pd) in meta.items() if rg == "Europe" and "2010-01-01" <= pd <= "2020-12-31"]
    C = [a for a, (rg, pd) in meta.items() if "2015-01-01" <= pd <= "2015-12-31"]
    bchg = [a for a in changes if a in set(B)]
    cchg = [a for a in changes if a in set(C)]
    nb_new = sum(1 for a in B if majority.get(a, base.get(a)) == "Business")
    print(f"info only: {len(bchg)} changed articles in q3 B {bchg}; q3 would be {nb_new}/11")
    print(f"info only: {len(cchg)} changed articles in q4 C {cchg}")

    out = {
        "protocol": "audit_q2_r017/PROTOCOL.md",
        "input_sha256": sha,
        "pass_sha256": {k: hashlib.sha256(open(f"{D}/pass{k}.json", "rb").read()).hexdigest()
                        for k in "ABC"},
        "majority": {a: majority[a] for a in sorted(ids, key=int)},
        "votes": {a: votes[a] for a in sorted(ids, key=int)},
        "fallback": fallback,
        "changes_vs_r016": {a: {"from": base[a], "to": majority[a]} for a in changes},
        "q2_sci_count": n_sci,
        "q2_answer": round(n_sci / 111, 4),
        "q2_pass": n_sci == 16,
    }
    json.dump(out, open(f"{D}/ADOPTION.json", "w"), indent=1, sort_keys=True)
    print(f"wrote {D}/ADOPTION.json")


if __name__ == "__main__":
    main()
