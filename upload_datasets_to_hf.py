#!/usr/bin/env python
"""Upload all DataAgentBench dataset files to the Hugging Face Hub.

This mirrors every file listed in ``dataset_manifest.tsv`` to a Hugging Face
*dataset* repo, preserving the relative paths so that ``download.sh`` can pull
them straight back into place.

Run once (per data refresh) from the repo root:

    export HF_TOKEN=hf_xxx          # token with write access to the org repo
    python upload_datasets_to_hf.py --create

Re-running is safe: by default the HF upload de-duplicates unchanged files.

Requires: pip install "huggingface_hub>=0.23"
"""
import argparse
import os
import sys

from huggingface_hub import HfApi, create_repo

DEFAULT_REPO = "ruiyingm/DataAgentBench-data"
DEFAULT_MANIFEST = "dataset_manifest.tsv"


def load_manifest(path):
    entries = []
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            rel, digest, size = line.split("\t")
            entries.append((rel, digest, int(size)))
    return entries


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-id", default=DEFAULT_REPO)
    ap.add_argument("--manifest", default=DEFAULT_MANIFEST)
    ap.add_argument("--token", default=os.environ.get("HF_TOKEN"))
    ap.add_argument("--create", action="store_true",
                    help="create the dataset repo if it does not exist")
    ap.add_argument("--private", action="store_true",
                    help="create the repo as private (default: public)")
    args = ap.parse_args()

    if not args.token:
        sys.exit("ERROR: provide a write token via --token or $HF_TOKEN")

    entries = load_manifest(args.manifest)
    missing = [rel for rel, _, _ in entries if not os.path.isfile(rel)]
    if missing:
        print("WARNING: these manifest files are missing locally and will be "
              "skipped:")
        for m in missing:
            print(f"  - {m}")
        entries = [e for e in entries if e[0] not in set(missing)]

    api = HfApi(token=args.token)

    if args.create:
        create_repo(args.repo_id, repo_type="dataset", token=args.token,
                    private=args.private, exist_ok=True)
        print(f"Repo ready: https://huggingface.co/datasets/{args.repo_id}")

    total = len(entries)
    for i, (rel, _digest, size) in enumerate(entries, 1):
        print(f"[{i}/{total}] uploading {rel} ({size / 1e6:.1f} MB) ...")
        api.upload_file(
            path_or_fileobj=rel,
            path_in_repo=rel,
            repo_id=args.repo_id,
            repo_type="dataset",
            commit_message=f"Add {rel}",
        )

    print(f"\nDone. Uploaded {total} files to {args.repo_id}.")


if __name__ == "__main__":
    main()
