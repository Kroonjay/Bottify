import sqlalchemy as sa
from core.config import settings


def get_trade_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "trade",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "bottify_order_id", sa.ForeignKey("bottify_order.id"), nullable=False
        ),
        sa.Column("source_id", sa.String(length=120), unique=True, nullable=False),
        sa.Column("is_taker", sa.Boolean),
        sa.Column(
            "price",
            sa.Numeric(
                precision=settings.BalanceMaximumDigits,
                scale=settings.BalanceDecimalPrecision,
                asdecimal=True,
                decimal_return_scale=settings.BalanceDecimalPrecision,
            ),
            nullable=False,
        ),
        sa.Column(
            "quantity",
            sa.Numeric(
                precision=settings.BalanceMaximumDigits,
                scale=settings.BalanceDecimalPrecision,
                asdecimal=True,
                decimal_return_scale=settings.BalanceDecimalPrecision,
            ),
            nullable=False,
        ),
        sa.Column(
            "fee",
            sa.Numeric(
                precision=settings.BalanceMaximumDigits,
                scale=settings.BalanceDecimalPrecision,
                asdecimal=True,
                decimal_return_scale=settings.BalanceDecimalPrecision,
            ),
            nullable=False,
        ),
        sa.Column("executed_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
