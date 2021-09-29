from databases import Database
from pydantic import BaseModel
from sqlalchemy import create_engine
from core.config import settings
import os
import logging

database = Database(str(settings.MainDatabase))

engine = create_engine(str(settings.MainDatabase))


# Used by Application methods that share a persistent Database connection
def get_db():
    return database


# Need to deprecate this
# Used by Worker and other processes that only need a temporary connection, used inside of with context block.  Number of connections significantly reduced, could possibly be increased but not sure by how much
def create_db():
    return Database(str(settings.MainDatabase), min_size=1, max_size=2)


def get_sync_db():
    return engine
