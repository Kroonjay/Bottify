import sqlalchemy as sa
from core.config import BALANCE_DECIMAL_PRECISION, BALANCE_MAXIMUM_DIGITS


def get_budget_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "budget",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("currency_id", sa.ForeignKey("currency.id"), nullable=False),
        sa.Column("exchange_id", sa.ForeignKey("exchange.id"), nullable=False),
        sa.Column("strategy_id", sa.ForeignKey("strategy.id"), nullable=False),
        sa.Column(
            "available",
            sa.Numeric(
                precision=BALANCE_MAXIMUM_DIGITS,
                scale=BALANCE_DECIMAL_PRECISION,
                asdecimal=True,
                decimal_return_scale=BALANCE_DECIMAL_PRECISION,
            ),
            nullable=False,
        ),
        sa.Column(
            "reserved",
            sa.Numeric(
                precision=BALANCE_MAXIMUM_DIGITS,
                scale=BALANCE_DECIMAL_PRECISION,
                asdecimal=True,
                decimal_return_scale=BALANCE_DECIMAL_PRECISION,
            ),
            nullable=False,
        ),
        sa.Column(
            "total",
            sa.Numeric(
                precision=BALANCE_MAXIMUM_DIGITS,
                scale=BALANCE_DECIMAL_PRECISION,
                asdecimal=True,
                decimal_return_scale=BALANCE_DECIMAL_PRECISION,
            ),
            sa.Computed("available + reserved"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "currency_id", "exchange_id", "strategy_id", name="budget_uc"
        ),
    )