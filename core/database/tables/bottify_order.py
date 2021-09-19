import sqlalchemy as sa
from core.config import BALANCE_DECIMAL_PRECISION, BALANCE_MAXIMUM_DIGITS


def get_bottify_order_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "bottify_order",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "order_guid", sa.dialects.postgresql.UUID, unique=True, nullable=False
        ),
        sa.Column(
            "source_id", sa.String(length=120), nullable=False
        ),  # Still not sure if this should be a UUID...keeping it as a String in case an exchange doesn't support UUID's
        sa.Column("strategy_id", sa.ForeignKey("strategy.id"), nullable=False),
        sa.Column("market_id", sa.ForeignKey("market.id"), nullable=False),
        sa.Column("status", sa.Integer, nullable=False),
        sa.Column("direction", sa.Integer, nullable=False),
        sa.Column("order_type", sa.Integer, nullable=False),
        sa.Column(
            "price",
            sa.Numeric(
                precision=BALANCE_MAXIMUM_DIGITS,
                scale=BALANCE_DECIMAL_PRECISION,
                asdecimal=True,
                decimal_return_scale=BALANCE_DECIMAL_PRECISION,
            ),
            nullable=False,
        ),
        sa.Column(
            "quantity",
            sa.Numeric(
                precision=BALANCE_MAXIMUM_DIGITS,
                scale=BALANCE_DECIMAL_PRECISION,
                asdecimal=True,
                decimal_return_scale=BALANCE_DECIMAL_PRECISION,
            ),
            nullable=False,
        ),
        sa.Column("time_in_force", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
