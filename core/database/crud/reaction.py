from databases import Database
from sqlalchemy import and_
import logging

from core.enums.alert_type import AlertType
from core.database.helpers import build_model_from_row, write_db
from core.database.tables.reaction import get_reaction_table
from core.models.reaction import (
    ReactionInModel,
    ReactionModel,
)

reaction_table = get_reaction_table()
logger = logging.getLogger("Bottify : CRUD : Reaction")


async def create_reaction(database: Database, reaction_in: ReactionInModel):
    if not isinstance(reaction_in, ReactionInModel):
        logger.error(
            f"Create Alert Reaction : Input Must be ReactionInModel : Got {type(reaction_in)}"
        )
        return False
    query = reaction_table.insert()
    return await write_db(database, query, reaction_in.dict())


async def read_reaction_by_id(database: Database, reaction_id: int):
    if not isinstance(reaction_id, int):
        logger.error(
            f"Read Alert Reaction by ID : ID Must be an Integer : Got {type(reaction_id)}"
        )
        return None
    query = reaction_table.select().where(reaction_table.c.id == reaction_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, ReactionModel)


async def read_all_reactions(database: Database, limit: int):
    reactions = []
    if not isinstance(limit, int):
        logger.error(
            f"Read All Reactions : Limit Must be an Integer : Got {type(limit)}"
        )
        return reactions
    query = reaction_table.select().limit(limit)
    async for row in database.iterate(query):
        reactions.append(build_model_from_row(row, ReactionModel))
    if not reactions:
        logger.error("Read All Reactions : No Results")
    return reactions


async def read_reactions_by_monitor_id(database: Database, monitor_id: int):
    results = []
    if not isinstance(monitor_id, int):
        logger.error(
            f"Read Alert Subscription by Monitor ID : Monitor ID Must be an Integer : Got {type(monitor_id)}"
        )
        return results
    query = reaction_table.select().where(reaction_table.c.monitor_id == monitor_id)
    async for row in database.iterate(query):
        results.append(build_model_from_row(row, ReactionModel))
    if not results:
        logger.error(f"Read Alert Subscriptions By Monitor ID : No Results")
    return results


async def read_reactions_by_alert_type(database: Database, alert_type: AlertType):
    results = []
    if not isinstance(alert_type, AlertType):
        logger.error(
            f"Read Alert Reactions by Alert Type : Alert Type Must be an AlertType Enum Member : Got {type(alert_type)}"
        )
        return results
    query = reaction_table.select().where(
        reaction_table.c.alert_type == alert_type.value
    )
    async for row in database.iterate(query):
        results.append(build_model_from_row(row, ReactionModel))
    if not results:
        logger.error(f"Read Alert Reactions by Alert Type : No Results")
    return results
