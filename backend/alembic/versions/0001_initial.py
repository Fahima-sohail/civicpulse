"""create civicpulse complaints

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

# The migration owns type creation below.  The table columns must reuse these types
# without issuing another CREATE TYPE during op.create_table().
category = postgresql.ENUM(
    "water", "electricity", "sanitation", "roads", "streetlights", "other",
    name="category", create_type=False,
)
priority = postgresql.ENUM("high", "normal", "low", name="priority", create_type=False)
status = postgresql.ENUM(
    "open", "in_progress", "resolved", "rejected", name="status", create_type=False,
)

def upgrade() -> None:
    bind = op.get_bind()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    category.create(bind, checkfirst=True)
    priority.create(bind, checkfirst=True)
    status.create(bind, checkfirst=True)
    op.create_table(
        "complaints",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("location", sa.String(200), nullable=False),
        sa.Column("reporter_contact", sa.String(255), nullable=True),
        sa.Column("category", category, nullable=False),
        sa.Column("priority", priority, nullable=False),
        sa.Column("status", status, nullable=False, server_default="open"),
        sa.Column("ai_summary", sa.String(140), nullable=True),
        sa.Column("triaged_by", sa.String(32), nullable=False),
        sa.Column("triage_latency_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("timezone('utc', now())")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("timezone('utc', now())")),
        sa.CheckConstraint("char_length(text) BETWEEN 10 AND 2000", name="ck_complaints_text_length"),
        sa.CheckConstraint("char_length(location) BETWEEN 3 AND 200", name="ck_complaints_location_length"),
        sa.PrimaryKeyConstraint("id"),
    )
    # Serves filtered operations-list queries ordered by status and priority.
    op.create_index("ix_complaints_status_priority", "complaints", ["status", "priority"])
    # Serves newest-first complaint listings and time-window operational queries.
    op.create_index("ix_complaints_created_at", "complaints", ["created_at"])

def downgrade() -> None:
    op.drop_index("ix_complaints_created_at", table_name="complaints")
    op.drop_index("ix_complaints_status_priority", table_name="complaints")
    op.drop_table("complaints")
    bind = op.get_bind()
    status.drop(bind, checkfirst=True)
    priority.drop(bind, checkfirst=True)
    category.drop(bind, checkfirst=True)
