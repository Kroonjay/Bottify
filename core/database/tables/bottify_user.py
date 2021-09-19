import sqlalchemy as sa


def get_bottify_user_table(meta=None):
    if not meta:
        meta = (
            sa.MetaData()
        )  # Must pass in metadata when creating tables, but we don't need it for running queries
    return sa.Table(
        "bottify_user",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("guid", sa.dialects.postgresql.UUID, unique=True, nullable=False),
        sa.Column("username", sa.String(length=90), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(length=120)),
        sa.Column("email", sa.String(length=254), unique=True),
        sa.Column("status", sa.Integer, nullable=False),
        sa.Column("user_role", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
