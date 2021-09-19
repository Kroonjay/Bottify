import sqlalchemy as sa


def get_indicator_definition_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "indicator_definition",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=90), unique=True, nullable=False),
        sa.Column("monitor_id", sa.String(length=90), unique=True),
        sa.Column("status", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("monitor_config", sa.Text),
        sa.Column("alert_params", sa.Text),
    )
