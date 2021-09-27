from databases import Database
from pydantic import BaseModel
from sqlalchemy import create_engine
from core.configs.db_config import MAIN_DB_CONN_STRING
import os
import logging

database = Database(MAIN_DB_CONN_STRING)

engine = create_engine(MAIN_DB_CONN_STRING)


# Used by Application methods that share a persistent Database connection
def get_db():
    return database


# Used by Worker and other processes that only need a temporary connection, used inside of with context block.  Number of connections significantly reduced, could possibly be increased but not sure by how much
def create_db():
    return Database(MAIN_DB_CONN_STRING, min_size=1, max_size=2)


def get_sync_db():
    return engine
