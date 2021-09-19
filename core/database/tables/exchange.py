import sqlalchemy as sa


def get_exchange_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "exchange",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=90), unique=True, nullable=False),
        sa.Column("user_id", sa.ForeignKey("bottify_user.id"), nullable=False),
        sa.Column("exchange_type", sa.Integer, nullable=False),
        sa.Column("status", sa.Integer, nullable=False),
        sa.Column("base_url", sa.String(length=254), nullable=False),
        sa.Column("auth", sa.Text),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
