import uuid
from datetime import datetime

from sqlalchemy import Float, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class ResponseStatus(str, enum.Enum):
    NOTIFIED = "notified"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    SNOOZED = "snoozed"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class DonorResponse(Base):
    __tablename__ = "donor_responses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("blood_requests.id"), nullable=False
    )
    donor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[ResponseStatus] = mapped_column(
        SAEnum(ResponseStatus), default=ResponseStatus.NOTIFIED
    )
    rank_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    notified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    blood_request = relationship("BloodRequest", back_populates="donor_responses")
    donor = relationship("User", back_populates="donor_responses")
    rating = relationship("Rating", back_populates="response", uselist=False)
