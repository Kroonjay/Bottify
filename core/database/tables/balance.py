import sqlalchemy as sa
from core.config import settings


def calculate_total_balance(context):
    return context.get_current_parameters()


def get_balance_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "balance",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("currency_id", sa.ForeignKey("currency.id"), nullable=False),
        sa.Column("exchange_id", sa.ForeignKey("exchange.id"), nullable=False),
        sa.Column(
            "available",
            sa.Numeric(
                precision=settings.BalanceMaximumDigits,
                scale=settings.BalanceDecimalPrecision,
                asdecimal=True,
                decimal_return_scale=settings.BalanceDecimalPrecision,
            ),
            nullable=False,
        ),
        sa.Column(
            "reserved",
            sa.Numeric(
                precision=settings.BalanceMaximumDigits,
                scale=settings.BalanceDecimalPrecision,
                asdecimal=True,
                decimal_return_scale=settings.BalanceDecimalPrecision,
            ),
            nullable=False,
        ),
        sa.Column(
            "total",
            sa.Numeric(
                precision=settings.BalanceMaximumDigits,
                scale=settings.BalanceDecimalPrecision,
                asdecimal=True,
                decimal_return_scale=settings.BalanceDecimalPrecision,
            ),
            sa.Computed("available + reserved"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.UniqueConstraint("currency_id", "exchange_id", name="balance_uc"),
    )
