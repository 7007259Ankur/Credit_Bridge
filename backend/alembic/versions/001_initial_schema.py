"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email_encrypted", sa.String, unique=True, nullable=False),
        sa.Column("email_hash", sa.String, unique=True, nullable=False),
        sa.Column("password_hash", sa.String, nullable=False),
        sa.Column("full_name_encrypted", sa.String, nullable=True),
        sa.Column("role", sa.Enum("applicant", "bank_officer", "admin", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    # consents
    op.create_table(
        "consents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("source_type", sa.Enum("phone", "ecommerce", "bank", "merchant", "geo",
                                          "psychometric", name="sourcetype"), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_consents_user_id", "consents", ["user_id"])

    # scoring_runs
    op.create_table(
        "scoring_runs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("celery_task_id", sa.String, nullable=True),
        sa.Column("status", sa.Enum("pending", "running", "completed", "failed",
                                     name="runstatus"), default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # agent_scores
    op.create_table(
        "agent_scores",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("run_id", sa.Integer, sa.ForeignKey("scoring_runs.id"), nullable=False),
        sa.Column("agent_name", sa.String, nullable=False),
        sa.Column("raw_score", sa.Float, nullable=False),
        sa.Column("weight", sa.Float, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("explanation", sa.String, nullable=False),
        sa.Column("signals", postgresql.JSON, nullable=True),
        sa.Column("data_snapshot", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    # credit_scores
    op.create_table(
        "credit_scores",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("run_id", sa.Integer, sa.ForeignKey("scoring_runs.id"), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("final_score", sa.Integer, nullable=False),
        sa.Column("score_band", sa.Enum("poor", "fair", "good", "very_good", "exceptional",
                                         name="scoreband"), nullable=False),
        sa.Column("recommendation", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_credit_scores_user_id", "credit_scores", ["user_id"])

    # audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("metadata", postgresql.JSON, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True)),
    )


def downgrade():
    op.drop_table("audit_log")
    op.drop_table("credit_scores")
    op.drop_table("agent_scores")
    op.drop_table("scoring_runs")
    op.drop_table("consents")
    op.drop_table("users")
