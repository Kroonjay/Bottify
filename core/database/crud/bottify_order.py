import logging

from databases import Database
from sqlalchemy import or_
from core.database.helpers import build_model_from_row, write_db
from core.database.tables.bottify_order import get_bottify_order_table
from core.models.order import BottifyOrderInModel, BottifyOrderModel
from core.enums.statuses import BottifyStatus

order_table = get_bottify_order_table()


async def create_order(database: Database, order_in: BottifyOrderInModel):
    if not isinstance(order_in, BottifyOrderInModel):
        logging.error(
            f"Create Order : Input Must be a BottifyOrderInModel : Got {type(order_in)}"
        )
        return False
    query = order_table.insert()
    return await write_db(database, query, order_in.dict())


async def read_all_orders(database: Database, limit: int):
    orders = []
    if not isinstance(limit, int):
        logging.error(f"Read All Orders : Limit Must be an Integer : Got {type(limit)}")
        return orders
    query = order_table.select().limit(limit)
    async for row in database.iterate(query):
        orders.append(build_model_from_row(row, BottifyOrderModel))
    if not orders:
        logging.error(f"Read All Orders : No Results")
    return orders


async def read_order_by_id(database: Database, order_id: int):
    if not isinstance(order_id, int):
        logging.error(
            f"Read Order by ID : ID Must be an Integer : Got {type(order_id)}"
        )
        return None
    query = order_table.select().where(order_table.c.id == order_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, BottifyOrderModel)


async def read_orders_by_status(database: Database, order_status: BottifyStatus):
    orders = []
    if not isinstance(order_status, BottifyStatus):
        logging.error(
            f"Read Orders by Status : Order Status Must be member of BottifyStatus : Got {type(order_status)}"
        )
        return orders
    query = order_table.select().where(order_table.c.status == order_status.value)
    async for row in database.iterate(query):
        orders.append(build_model_from_row(row, BottifyOrderModel))
    if not orders:
        logging.error("Read Orders by Status : No Results")
    return orders


async def read_open_orders(database: Database):
    orders = []
    query = order_table.select().where(
        or_(
            order_table.c.status == BottifyStatus.Active.value,
            order_table.c.status == BottifyStatus.New.value,
        )
    )
    async for row in database.iterate(query):
        orders.append(build_model_from_row(row, BottifyOrderModel))
    if not orders:
        logging.error("Read Open Orders : No Results")
    return orders


async def update_order_status(
    database: Database, order_id: int, new_status: BottifyStatus
):
    success = False
    if not isinstance(new_status, BottifyStatus):
        if isinstance(new_status, int):
            try:
                new_status = BottifyStatus(new_status)
            except ValueError as ve:
                logging.error(
                    f"Update Order Status : New Status is an Int but Not a Member of BottifyStatus : Got {str(new_status)}"
                )
                return success
        else:
            logging.error(
                f"Update Order Status : New Status must be either BottifyStatus enum or Int : Got {type(new_status)}"
            )
            return success
    if not isinstance(order_id, int):
        logging.error(
            f"Update Order Status : Order ID Must be an Integer : Got {type(order_id)}"
        )
        return success
    query = (
        order_table.update()
        .where(order_table.c.id == order_id)
        .values({"status": new_status.value})
    )
    await database.execute(query)
    success = True  # TODO Write an exec_db function to wrap this
    return success
