import sqlalchemy as sa


def get_monitor_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "monitor",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("source_id", sa.String(length=120), unique=True, nullable=False),
        sa.Column("status", sa.Integer, nullable=False),
        sa.Column("severity", sa.Integer, nullable=False),
        sa.Column("alert_interval", sa.Integer),
        sa.Column("indices", sa.Text, nullable=False),
        sa.Column("queries", sa.Text, nullable=False),
        sa.Column("definition", sa.Text, nullable=False),
        sa.Column("notes", sa.Text),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
