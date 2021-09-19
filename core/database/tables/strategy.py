import sqlalchemy as sa


def get_strategy_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "strategy",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("guid", sa.dialects.postgresql.UUID, unique=True, nullable=False),
        sa.Column("name", sa.String(length=90), nullable=False, unique=True),
        sa.Column("user_id", sa.ForeignKey("bottify_user.id"), nullable=False),
        sa.Column("base_currency_id", sa.ForeignKey("currency.id"), nullable=False),
        sa.Column("status", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True)),
        sa.Column(
            "config", sa.Text
        ),  # Keeping this as text as budgets may exceed char limits, reserving the space for future configs
    )
