"""Initial schema — users, blood_requests, donor_responses, ratings, fraud_flags

Revision ID: 001
Revises: None
Create Date: 2026-10-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=True, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("donor", "requester", "admin", name="userrole"), nullable=False, server_default="donor"),
        sa.Column("blood_group", sa.Enum("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", name="bloodgroup"), nullable=True),
        sa.Column("area", sa.String(100), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("last_donation_date", sa.DateTime, nullable=True),
        sa.Column("is_available", sa.Boolean, server_default="true"),
        sa.Column("preferred_hours_start", sa.Integer, nullable=True),
        sa.Column("preferred_hours_end", sa.Integer, nullable=True),
        sa.Column("reliability_score", sa.Float, server_default="50.0"),
        sa.Column("is_phone_verified", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_phone", "users", ["phone"])
    op.create_index("ix_users_blood_group", "users", ["blood_group"])
    op.create_index("ix_users_area", "users", ["area"])

    # --- Blood Requests ---
    op.create_table(
        "blood_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("requester_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("patient_name", sa.String(100), nullable=False),
        sa.Column("blood_group_needed", sa.Enum("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", name="bloodgroup", create_type=False), nullable=False),
        sa.Column("units_needed", sa.Integer, server_default="1"),
        sa.Column("units_fulfilled", sa.Integer, server_default="0"),
        sa.Column("hospital_name", sa.String(200), nullable=False),
        sa.Column("hospital_address", sa.String(300), nullable=True),
        sa.Column("hospital_latitude", sa.Float, nullable=True),
        sa.Column("hospital_longitude", sa.Float, nullable=True),
        sa.Column("urgency", sa.Enum("routine", "urgent", "emergency", name="urgencylevel"), server_default="urgent"),
        sa.Column("status", sa.Enum("open", "partially_fulfilled", "fulfilled", "expired", "cancelled", name="requeststatus"), server_default="open"),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_blood_requests_status", "blood_requests", ["status"])
    op.create_index("ix_blood_requests_blood_group", "blood_requests", ["blood_group_needed"])
    op.create_index("ix_blood_requests_urgency", "blood_requests", ["urgency"])

    # --- Donor Responses ---
    op.create_table(
        "donor_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("blood_requests.id"), nullable=False),
        sa.Column("donor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.Enum("notified", "accepted", "declined", "snoozed", "completed", "no_show", name="responsestatus"), server_default="notified"),
        sa.Column("rank_score", sa.Float, nullable=True),
        sa.Column("notified_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_donor_responses_request", "donor_responses", ["request_id"])
    op.create_index("ix_donor_responses_donor", "donor_responses", ["donor_id"])

    # --- Ratings ---
    op.create_table(
        "ratings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("response_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("donor_responses.id"), nullable=False),
        sa.Column("rated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("rated_user", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("comment", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- Fraud Flags ---
    op.create_table(
        "fraud_flags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("blood_requests.id"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("flag_type", sa.String(50), nullable=False),
        sa.Column("details", sa.String(500), nullable=True),
        sa.Column("status", sa.Enum("pending", "reviewed", "dismissed", "actioned", name="flagstatus"), server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("fraud_flags")
    op.drop_table("ratings")
    op.drop_table("donor_responses")
    op.drop_table("blood_requests")
    op.drop_table("users")

    # Drop enums
    for name in ["flagstatus", "responsestatus", "requeststatus", "urgencylevel", "bloodgroup", "userrole"]:
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
