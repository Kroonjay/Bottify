import sqlalchemy as sa
from core.config import BALANCE_DECIMAL_PRECISION, BALANCE_MAXIMUM_DIGITS


def get_alert_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "alert",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("source_id", sa.String(length=120), nullable=False),
        sa.Column("monitor_id", sa.String(length=254), nullable=False),
        sa.Column("trigger_id", sa.String(length=120), nullable=False),
        sa.Column("status", sa.Integer, nullable=False),
        sa.Column("severity", sa.Integer, nullable=False),
        sa.Column("period_start", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("period_end", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("total_results", sa.Integer, nullable=False),
        sa.Column(
            "monitor_id",
            sa.ForeignKey("monitor.id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("exchange", sa.String(length=120)),
        sa.Column("currency", sa.String(length=120)),
        sa.Column("market", sa.String(length=120)),
        sa.Column(
            "price",
            sa.Numeric(
                precision=BALANCE_MAXIMUM_DIGITS,
                scale=BALANCE_DECIMAL_PRECISION,
                asdecimal=True,
                decimal_return_scale=BALANCE_DECIMAL_PRECISION,
            ),
        ),
    )
