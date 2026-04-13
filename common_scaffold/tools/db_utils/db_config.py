import os
from dotenv import load_dotenv
import yaml
from bson import ObjectId
import pandas as pd
import numpy as np
from bson import ObjectId
from datetime import datetime, date
from enum import Enum

load_dotenv()

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
# Path to mongorestore (MongoDB Database Tools); use full path if not on PATH
MONGORESTORE = os.getenv("MONGORESTORE", "mongorestore")

# SQLite
SQLITE_PATH = os.getenv("SQLITE_PATH", "data/mydb.sqlite")
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "data/mydb.duckdb")

# PostgreSQL
PG_CLIENT = os.getenv("PG_CLIENT", "psql")
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = int(os.getenv("PG_PORT", 5432))
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")
PG_DB = os.getenv("PG_DB", "test")

def load_db_clients(config_file: str):
    with open(config_file, "r") as f:
        db_clients = yaml.safe_load(f)['db_clients']
    
    for db_client in db_clients.values():
        for key in ['db_path', 'dump_folder', 'sql_file']:
            if key in db_client:
                db_path = os.path.join(os.path.dirname(config_file), db_client[key])
                assert os.path.exists(db_path), f"{key} does not exist: {db_path}"
                db_client[key] = db_path
    return db_clients

# def serialize(obj):
#     """Serialize pandas DataFrame and ObjectId to JSON-serializable formats."""
#     if isinstance(obj, pd.DataFrame):
#         obj_dict = obj.to_dict(orient='records')
#         return serialize(obj_dict)
#     elif isinstance(obj, ObjectId): # mongo
#         return str(obj)
#     elif isinstance(obj, dict):
#         return {k: serialize(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [serialize(v) for v in obj]
#     else:
#         return obj

def serialize(obj):
    """Recursively convert objects into JSON-serializable structures."""
    
    # --- Pandas ---
    if isinstance(obj, pd.DataFrame):
        return [serialize(row) for row in obj.to_dict(orient='records')]
    if isinstance(obj, pd.Series):
        return serialize(obj.to_dict())
    if isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return str(obj)

    # --- Numpy ---
    if isinstance(obj, (np.integer, )):
        return int(obj)
    if isinstance(obj, (np.floating, )):
        return float(obj)
    if isinstance(obj, (np.ndarray, )):
        return serialize(obj.tolist())
    if isinstance(obj, (np.datetime64, )):
        return str(pd.to_datetime(obj))

    # --- Datetime / Date ---
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    # --- Mongo ---
    if isinstance(obj, ObjectId):
        return str(obj)

    # --- Collections ---
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [serialize(v) for v in obj]

    # --- Enum ---
    if isinstance(obj, Enum):
        return obj.value

    # --- SQLAlchemy row object ---
    if hasattr(obj, "_asdict"):  # RowMapping or row tuple
        return serialize(obj._asdict())
    if hasattr(obj, "__dict__") and not isinstance(obj, type):
        # Avoid serializing class definitions or modules
        return serialize(vars(obj))

    # --- Fallback: try to convert unknown object ---
    try:
        return str(obj)
    except Exception:
        return repr(obj)
