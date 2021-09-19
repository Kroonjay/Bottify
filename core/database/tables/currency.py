import sqlalchemy as sa


def get_currency_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "currency",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("symbol", sa.String(length=10), unique=True, nullable=False),
        sa.Column("currency_type", sa.Integer, nullable=False),
        sa.Column("status", sa.Integer, nullable=False),
        sa.Column("tags", sa.Text),
        sa.Column("token_address", sa.String(length=254)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True)),
    )
