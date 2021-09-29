import sqlalchemy as sa
from core.config import settings


def get_market_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "market",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("base_currency_id", sa.ForeignKey("currency.id"), nullable=False),
        sa.Column("quote_currency_id", sa.ForeignKey("currency.id"), nullable=False),
        sa.Column("exchange_id", sa.ForeignKey("exchange.id"), nullable=False),
        sa.Column("symbol", sa.String(length=10), nullable=False),
        sa.Column("status", sa.Integer, nullable=False),
        sa.Column(
            "min_trade_size",
            sa.Numeric(
                precision=settings.BalanceMaximumDigits,
                scale=settings.BalanceDecimalPrecision,
                asdecimal=True,
                decimal_return_scale=settings.BalanceDecimalPrecision,
            ),
            nullable=False,
        ),
        sa.Column("notice", sa.String(length=200)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("tags", sa.Text),
    )
