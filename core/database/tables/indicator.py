import sqlalchemy as sa


def get_indicator_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "indicator",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("strategy_id", sa.ForeignKey("strategy.id"), nullable=False),
        sa.Column(
            "definition_id", sa.ForeignKey("indicator_definition.id"), nullable=False
        ),
        sa.Column(
            "monitor_id", sa.String(length=90), nullable=False
        ),  # This should probably be a multi-column unique with strategy id but meh
        sa.Column("response_action", sa.Integer, nullable=False),
        sa.Column("status", sa.Integer, nullable=False),
    )
