import logging
from databases import Database
from core.database.helpers import build_model_from_row, write_db
from core.database.database import create_db
from core.database.tables.config_key import get_config_key_table
from core.models.config_keys import ConfigKeyModel, ConfigKeyInModel
from datetime import datetime, timezone
config_key_table = get_config_key_table()


async def create_config_key(database: Database, key_in: ConfigKeyInModel):
    if not isinstance(key_in, ConfigKeyInModel):
        logging.error(
            f"Create Config Key : Input Must be a ConfigKeyInModel : Got {type(key_in)}"
        )
        return False
    query = config_key_table.insert()
    await write_db(database, query, key_in.dict())
    return True

async def read_config_key_by_id(database: Database: key_id: int):
    if not isinstance(key_id, int):
        logging.error(f"Read Config Key by ID : ID Must be an Integer : Got {type(key_id)}")
        return None
    query = config_key_table.select().where(config_key_table.c.id == key_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, ConfigKeyModel)

async def read_config_key_by_name(database: Database, key_name: str):
    if not isinstance(key_name, str):
        logging.error(f"Read Config Key by Name : Key Name Must be a String : Got {type(key_name)}")
        return None
    query = config_key_table.select().where(config_key_table.c.name == key_name).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, ConfigKeyModel)

async def update_config_key_value(database: Database, key_id: int, new_value: str):
    if not isinstance(key_id, int):
        logging.error(f"Update Config Key Value : Key ID Must be an Integer : Got {type(key_id)}")
        return False
    if not isinstance(new_value, str):
        logging.error(f"Update Config Key Value : New Value Must be a String : Got {type(new_value)}")
        return False
    query = config_key_table.update().where(config_key_table.c.id == key_id).values({"value" : new_value, "modified_at" : datetime.now(tz=timezone.utc)})
    await database.execute(query)
    return True

async def exec_read_config_by_name(key_name: str):
    async with create_db() as database:
        return read_config_key_by_name(database, key_name)



def sync_read_config_key(key_name: str):
    if not isinstance(key_name, str):
        logging.error(f"Sync Read Config Key by Name : Key Name Must be a String : Got {type(key_name)}")
        return None
    config_key = asyncio.run(exec_read_config_by_name(key_name))
    if not config_key:
        logging.error(f"Sync Read Config Key by Name : No Results")
    return config_key