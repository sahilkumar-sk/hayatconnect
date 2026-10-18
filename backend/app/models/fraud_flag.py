import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.database import Base


class FlagStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
    ACTIONED = "actioned"


class FraudFlag(Base):
    __tablename__ = "fraud_flags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("blood_requests.id"), nullable=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    flag_type: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[FlagStatus] = mapped_column(
        SAEnum(FlagStatus, values_callable=lambda e: [m.value for m in e]), default=FlagStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
