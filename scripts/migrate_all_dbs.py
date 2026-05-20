#!/usr/bin/env python3
"""
Load all PostgreSQL and MongoDB datasets defined under query_*/db_config.yaml.

Uses the same logic as QueryDBTool (postgres_utils.load_db / mongo_utils.load_db).
Run from anywhere; switches cwd to repo root so .env is picked up.

Requires: psql on PATH (or PG_CLIENT), mongorestore on PATH (or MONGORESTORE in .env = full path),
PG_* and MONGO_URI in .env.

If MongoDB is not running, use --postgres-only or --skip-mongo-if-unreachable (otherwise the script exits before restores).
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

try:
    from common_scaffold.tools.db_utils import db_config, mongo_utils, postgres_utils  # noqa: E402
    from common_scaffold.tools.BaseTool import FatalError  # noqa: E402
except ImportError as e:
    print(
        "Missing dependencies (e.g. pandas). Activate the project conda env from environment.yaml, "
        "then run this script again.\n"
        f"ImportError: {e}",
        file=sys.stderr,
    )
    sys.exit(1)


def discover_db_configs() -> list[Path]:
    return sorted(REPO_ROOT.glob("query_*/db_config.yaml"))


def load_clients(config_path: Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("db_clients") or {}


def resolve_artifact(config_path: Path, rel: str) -> Path:
    return (config_path.parent / rel).resolve()


def mongo_reachable(timeout_ms: int = 4000) -> bool:
    """Quick ping; avoids repeated 30s ServerSelectionTimeout per client."""
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError

    client = MongoClient(db_config.MONGO_URI, serverSelectionTimeoutMS=timeout_ms)
    try:
        client.admin.command("ping")
        return True
    except PyMongoError:
        return False
    finally:
        client.close()


def migrate_postgres(config_path: Path, client_key: str, client: dict, dry_run: bool) -> None:
    sql_rel = client["sql_file"]
    db_name = client["db_name"]
    sql_path = resolve_artifact(config_path, sql_rel)
    if not sql_path.is_file():
        logging.warning("Skip postgres %s / %s: missing sql_file %s", config_path.parent.name, client_key, sql_path)
        return
    logging.info("Postgres %s / %s -> db=%s file=%s", config_path.parent.name, client_key, db_name, sql_path)
    if dry_run:
        return
    postgres_utils.load_db(str(sql_path), db_name)


def migrate_mongo(config_path: Path, client_key: str, client: dict, dry_run: bool) -> None:
    dump_rel = client["dump_folder"]
    db_name = client["db_name"]
    dump_path = resolve_artifact(config_path, dump_rel)
    if not dump_path.is_dir():
        logging.warning("Skip mongo %s / %s: missing dump_folder %s", config_path.parent.name, client_key, dump_path)
        return
    logging.info("Mongo %s / %s -> db=%s dir=%s", config_path.parent.name, client_key, db_name, dump_path)
    if dry_run:
        return
    mongo_utils.load_db(str(dump_path), db_name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Load all Postgres + MongoDB benchmark datasets.")
    parser.add_argument("--postgres-only", action="store_true", help="Only run PostgreSQL loads.")
    parser.add_argument("--mongo-only", action="store_true", help="Only run MongoDB loads.")
    parser.add_argument(
        "--skip-mongo-if-unreachable",
        action="store_true",
        help="If mongod is down, skip Mongo restores instead of failing (Postgres still runs).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without loading.")
    parser.add_argument("-v", "--verbose", action="store_true", help="DEBUG logging.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    do_pg = not args.mongo_only
    do_mongo = not args.postgres_only
    if args.postgres_only and args.mongo_only:
        logging.error("Cannot combine --postgres-only and --mongo-only.")
        return 2

    configs = discover_db_configs()
    if not configs:
        logging.error("No query_*/db_config.yaml found under %s", REPO_ROOT)
        return 1

    logging.info("Repo root: %s", REPO_ROOT)
    logging.info("Found %d db_config.yaml file(s).", len(configs))

    if do_mongo and not args.dry_run:
        if mongo_reachable():
            logging.debug("MongoDB ping OK (%s)", db_config.MONGO_URI)
        elif args.skip_mongo_if_unreachable:
            logging.warning(
                "MongoDB not reachable at %s; skipping all Mongo restores (--skip-mongo-if-unreachable).",
                db_config.MONGO_URI,
            )
            do_mongo = False
        else:
            logging.error(
                "MongoDB not reachable at %s (connection refused or timeout). "
                "Start mongod, then re-run, or use --postgres-only / --skip-mongo-if-unreachable.",
                db_config.MONGO_URI,
            )
            return 3

    if args.mongo_only and not do_mongo:
        logging.error("Mongo-only run cannot proceed (MongoDB unreachable or skipped).")
        return 3

    failed: list[str] = []
    for config_path in configs:
        try:
            clients = load_clients(config_path)
        except Exception as e:
            logging.error("Failed to read %s: %s", config_path, e)
            failed.append(str(config_path))
            continue

        for client_key, client in clients.items():
            db_type = client.get("db_type")
            try:
                if db_type == "postgres" and do_pg:
                    migrate_postgres(config_path, client_key, client, args.dry_run)
                elif db_type == "mongo" and do_mongo:
                    migrate_mongo(config_path, client_key, client, args.dry_run)
            except FatalError as e:
                logging.error("%s / %s: %s", config_path.parent.name, client_key, e)
                failed.append(f"{config_path}:{client_key}")

    if failed:
        logging.error("Finished with %d error(s).", len(failed))
        return 1
    logging.info("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
