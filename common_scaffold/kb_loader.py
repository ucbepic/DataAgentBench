"""
KB Loader — loads oracle-forge knowledge base files and filters by dataset.

Loads three categories of KB content:
  1. Corrections log (kb/corrections/log.md) — past failure patterns
  2. Join key glossary (kb/domain/join_key_glossary.md) — cross-DB join rules
  3. Schemas (kb/domain/schemas.md) — column semantics per dataset

Filtering: corrections and schemas are filtered to only include sections
relevant to the target dataset, keeping the context window lean.
"""

import re
from pathlib import Path
from typing import Optional


# Map DAB dataset names to the section headers / dataset tags used in KB files
DATASET_KB_TAGS = {
    "bookreview": ["bookreview", "book_review"],
    "crmarenapro": ["crmarenapro", "crm"],
    "DEPS_DEV_V1": ["DEPS_DEV_V1", "deps_dev", "NPM"],
    "GITHUB_REPOS": ["GITHUB_REPOS", "github"],
    "googlelocal": ["googlelocal", "google_local", "Google Local"],
    "PANCANCER_ATLAS": ["PANCANCER_ATLAS", "pancancer", "PanCancer"],
    "PATENTS": ["PATENTS", "patents", "Patent"],
    "stockindex": ["stockindex", "stock_index", "Stock"],
    "stockmarket": ["stockmarket", "stock_market", "Stock"],
    "yelp": ["yelp", "Yelp"],
    "agnews": ["agnews", "ag_news", "AG News"],
    "music_brainz_20k": ["music_brainz", "MusicBrainz"],
}


def _filter_sections_by_dataset(content: str, dataset: str) -> str:
    """Extract only the sections relevant to a dataset from a markdown file.

    Splits on ## headings and keeps:
      - Everything before the first ## (preamble / instructions)
      - Any ## section whose heading or body mentions the dataset tags
    """
    tags = DATASET_KB_TAGS.get(dataset, [dataset])
    pattern = re.compile("|".join(re.escape(t) for t in tags), re.IGNORECASE)

    sections = re.split(r"(?=^## )", content, flags=re.MULTILINE)

    kept = []
    for section in sections:
        if not section.startswith("## "):
            # Preamble — always keep
            kept.append(section)
        elif pattern.search(section):
            kept.append(section)

    return "\n".join(kept).strip()


def load_kb(kb_dir: str | Path, dataset: Optional[str] = None) -> str:
    """Load KB content from the oracle-forge kb directory.

    Args:
        kb_dir: Path to the kb/ directory (e.g. ../oracle-forge-data-agent/kb)
        dataset: If provided, filter corrections and schemas to this dataset only.

    Returns:
        A single string with all KB context, ready for injection into the prompt.
    """
    kb_dir = Path(kb_dir)
    parts = []

    # 1. Corrections log — filtered by dataset
    corrections_path = kb_dir / "corrections" / "log.md"
    if corrections_path.exists():
        corrections = corrections_path.read_text(encoding="utf-8")
        if dataset:
            corrections = _filter_sections_by_dataset(corrections, dataset)
        if corrections.strip():
            parts.append(f"## CORRECTION MEMORY (past failure patterns)\n\n{corrections}")

    # 2. Join key glossary — always load in full (it's a lookup reference)
    glossary_path = kb_dir / "domain" / "join_key_glossary.md"
    if glossary_path.exists():
        glossary = glossary_path.read_text(encoding="utf-8")
        if dataset:
            glossary = _filter_sections_by_dataset(glossary, dataset)
        if glossary.strip():
            parts.append(f"## JOIN KEY GLOSSARY (cross-database join rules)\n\n{glossary}")

    # 3. Schemas — filtered by dataset
    schemas_path = kb_dir / "domain" / "schemas.md"
    if schemas_path.exists():
        schemas = schemas_path.read_text(encoding="utf-8")
        if dataset:
            schemas = _filter_sections_by_dataset(schemas, dataset)
        if schemas.strip():
            parts.append(f"## COLUMN SEMANTICS (what columns mean)\n\n{schemas}")

    # 4. Business terms — filtered by dataset
    terms_path = kb_dir / "domain" / "business_terms.md"
    if terms_path.exists():
        terms = terms_path.read_text(encoding="utf-8")
        if dataset:
            terms = _filter_sections_by_dataset(terms, dataset)
        if terms.strip():
            parts.append(f"## BUSINESS TERMS (domain definitions)\n\n{terms}")

    if not parts:
        return ""

    header = "# KNOWLEDGE BASE CONTEXT\n\n"
    header += "Use the following knowledge to avoid known failure patterns.\n"
    header += "Pay special attention to CORRECTION MEMORY — these are mistakes made in prior runs.\n\n"
    return header + "\n\n---\n\n".join(parts)


def load_corrections_log(corrections_path: str | Path) -> str:
    """Load a local corrections log file (used in self-correction loop)."""
    corrections_path = Path(corrections_path)
    if corrections_path.exists():
        return corrections_path.read_text(encoding="utf-8")
    return ""
