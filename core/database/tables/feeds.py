import sqlalchemy as sa


def get_feeds_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "feed",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("feed_type", sa.Integer),
        sa.Column("feed_name", sa.String(length=50), unique=True),
        sa.Column("index_name", sa.String(length=50)),
        sa.Column("update_interval", sa.Integer),
        sa.Column("status", sa.Integer),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("last_execution_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("next_execution_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("configs", sa.Text),
    )
