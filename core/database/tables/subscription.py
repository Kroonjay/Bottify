import sqlalchemy as sa


def get_subscription_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "subscription",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("monitor_id", sa.ForeignKey("monitor.id"), nullable=False),
        sa.Column("strategy_id", sa.ForeignKey("strategy.id"), nullable=False),
        sa.Column("reaction_id", sa.ForeignKey("reaction.id"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True)),
        sa.UniqueConstraint(
            "monitor_id", "strategy_id", "reaction_id", name="subscription_uc"
        ),
    )
