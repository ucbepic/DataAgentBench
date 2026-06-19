#!/usr/bin/env bash
set -euo pipefail

# DataAgentBench dataset downloader.
#
# All large dataset files (PostgreSQL dumps, SQLite/DuckDB databases, MongoDB
# BSON, etc.) are mirrored on the Hugging Face Hub instead of Git LFS. This
# script downloads every file listed in dataset_manifest.tsv into its correct
# location and verifies each one against the recorded sha256 checksum.
#
# Usage:
#   bash download.sh              # download any missing / wrong-sized files
#   VERIFY_ALL=1 bash download.sh # re-hash every existing file (slow, ~19GB)
#
# Re-running is safe: files already present with the expected size are skipped.

REPO_ID="${DAB_HF_REPO:-ruiyingm/DataAgentBench-data}"
MANIFEST="${DAB_MANIFEST:-dataset_manifest.tsv}"

cd "$(dirname "$0")"

if [ ! -f "$MANIFEST" ]; then
    echo "ERROR: manifest '$MANIFEST' not found (run from the repo root)." >&2
    exit 1
fi

# huggingface_hub powers the download. Auto-install if absent, mirroring the
# previous gdown bootstrap.
if ! python -c "import huggingface_hub" >/dev/null 2>&1; then
    echo "huggingface_hub not found. Installing..."
    pip install -q "huggingface_hub>=0.23"
fi

echo "Downloading datasets from https://huggingface.co/datasets/${REPO_ID}"

REPO_ID="$REPO_ID" MANIFEST="$MANIFEST" VERIFY_ALL="${VERIFY_ALL:-0}" python - <<'PY'
import hashlib
import os
import sys

from huggingface_hub import hf_hub_download

repo_id = os.environ["REPO_ID"]
manifest = os.environ["MANIFEST"]
verify_all = os.environ.get("VERIFY_ALL", "0") == "1"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


entries = []
with open(manifest) as f:
    for line in f:
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        path, digest, size = line.split("\t")
        entries.append((path, digest, int(size)))

downloaded = skipped = 0
failures = []

for path, digest, size in entries:
    # Skip if already present and the right size (and, when VERIFY_ALL, the
    # right hash). This avoids re-hashing ~19GB on every run.
    if os.path.isfile(path) and os.path.getsize(path) == size:
        if not verify_all or sha256(path) == digest:
            print(f"  [skip] {path}")
            skipped += 1
            continue

    print(f"  [get ] {path} ({size / 1e6:.1f} MB)")
    try:
        hf_hub_download(
            repo_id=repo_id,
            repo_type="dataset",
            filename=path,
            local_dir=".",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"  [FAIL] download error for {path}: {exc}")
        failures.append(path)
        continue

    actual = sha256(path)
    if actual != digest:
        print(f"  [FAIL] checksum mismatch for {path}")
        print(f"         expected {digest}")
        print(f"         actual   {actual}")
        failures.append(path)
        continue
    downloaded += 1

print()
print(f"Downloaded: {downloaded}, skipped: {skipped}, failed: {len(failures)}")
if failures:
    print("Failed files:")
    for p in failures:
        print(f"  - {p}")
    sys.exit(1)
print("All datasets present and verified.")
PY

echo "Done."
