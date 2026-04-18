import json
import pandas as pd
from pymongo import MongoClient
from common_scaffold.tools.db_utils import db_config
from common_scaffold.tools.BaseTool import FatalError
import subprocess
from pathlib import Path
import logging

"""
MongoDB Config:
- db_type
- db_name
- dump_folder
"""

# Reference: https://www.mongodb.com/docs/manual/administration/install-community/?linux-distribution=ubuntu&linux-package=default&operating-system=linux&search-linux=with-search-linux#start-mongodb-12

def load_db(dump_folder: str, db_name: str):
    if check_db_exists(db_name) == True:
        logging.getLogger(__name__).warning(f"Database '{db_name}' already exists. Cleaning up before loading dump.")
        clean_up(db_name)
        # raise FatalError(f"Database '{db_name}' already exists. Cannot load dump into existing database.")
    try:
        logging.getLogger(__name__).debug(f"Loading MongoDB dump from '{dump_folder}' into database '{db_name}'")
        dump_path = Path(dump_folder).resolve()
        if not dump_path.exists():
            raise FileNotFoundError(f"Dump folder not found: {dump_folder}")
        # subprocess.run(
        #     ["mongorestore", f"--nsInclude={db_name}.*", dump_path],
        #     check=True
        # )
        result = subprocess.run(
            ["mongorestore", f"--uri={db_config.MONGO_URI}", f"--nsInclude={db_name}.*", "--drop", str(dump_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout:
            logging.getLogger(__name__).debug(f"MongoDB load stdout: {result.stdout}")
        if result.stderr:
            logging.getLogger(__name__).warning(f"MongoDB load stderr: {result.stderr}")
    except Exception as e:
        raise FatalError(f"MongoDB load error ({type(e).__name__}): {str(e)}")

def check_db_exists(db_name):
    with MongoClient(db_config.MONGO_URI) as mongo_client:
        try:
            dbs = mongo_client.list_database_names()
            return db_name in dbs
        except Exception as e:
            raise FatalError(f"MongoDB existence check error ({type(e).__name__}): {str(e)}")

def clean_up(db_name):
    logging.getLogger(__name__).debug(f"Cleaning up MongoDB database '{db_name}'")
    with MongoClient(db_config.MONGO_URI) as mongo_client:
        try:
            if db_name in mongo_client.list_database_names():
                mongo_client.drop_database(db_name)
        except Exception as e:
            raise FatalError(f"MongoDB cleanup error ({type(e).__name__}): {str(e)}")
        


class MongoQueryDBTool:
    @staticmethod
    def check_args(db_client: dict, query: str):
        if 'db_name' not in db_client:
            raise FatalError(f"Missing `db_name` for mongo db_client: {db_client}")
        try:
            query_json = json.loads(query)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid Mongo query JSON ({type(e).__name__}): {str(e)}")
        if "collection" not in query_json:
            raise ValueError("Invalid Mongo query: missing required field `collection`")
        collection = query_json["collection"]
        filter = query_json.get("filter", {})
        projection = query_json.get("projection", None)
        limit = query_json.get("limit", None)
        return {
            "db_name": db_client['db_name'],
            "collection": collection,
            "filter": filter,
            "projection": projection,
            "limit": limit
        }

    @staticmethod
    def exec(db_name, collection, filter, projection, limit):
        with MongoClient(db_config.MONGO_URI) as mongo_client:
            db = mongo_client[db_name]

            if collection not in db.list_collection_names():
                raise ValueError(f"Collection does not exist: {collection}")
        
            try:
                cursor = db[collection].find(filter, projection)
                if limit is not None:
                    cursor = cursor.limit(limit)
                result = list(cursor)
            except Exception as e:
                raise ValueError(f"MongoDB query execution error ({type(e).__name__}): {str(e)}")
        
        if not result:
            result_df = pd.DataFrame()
        else:
            result_df = pd.DataFrame(result)

        return db_config.serialize(result_df)
        

class MongoListDBTool:
    @staticmethod
    def check_args(db_client: dict):
        if 'db_name' not in db_client:
            raise FatalError(f"Missing `db_name` for mongo db_client: {db_client}")
        return {
            "db_name": db_client['db_name']
        }
    
    @staticmethod
    def exec(db_name):
        with MongoClient(db_config.MONGO_URI) as mongo_client:
            db = mongo_client[db_name]
            try:
                collections = db.list_collection_names()
                return collections
            except Exception as e:
                raise FatalError(f"MongoDB list collections error ({type(e).__name__}): {str(e)}")