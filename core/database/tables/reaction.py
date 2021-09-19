import sqlalchemy as sa


def get_reaction_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "reaction",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("monitor_id", sa.ForeignKey("monitor.id"), nullable=False),
        sa.Column("direction", sa.Integer, nullable=False),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("time_in_force", sa.Integer, nullable=False),
        sa.Column("status", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
